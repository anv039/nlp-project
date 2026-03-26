import spacy
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import os
import re
import sys
import json

# Use the transformer model (most accurate)
MODEL_NAME = "en_core_web_trf"

# Load the model
print(f"Loading {MODEL_NAME}...")
try:
    nlp = spacy.load(MODEL_NAME)
    print(f"✅ Loaded {MODEL_NAME}")
except OSError:
    print(f"❌ Error: {MODEL_NAME} not found. Installing...")
    os.system(f"python -m spacy download {MODEL_NAME}")
    nlp = spacy.load(MODEL_NAME)

def clean_entity_name(name):
    """Clean up entity names by removing extra spaces and standardizing"""
    name = ' '.join(name.split())
    if name == '-' or name.startswith('-') or name.endswith('-'):
        return None
    return name

def extract_entities(text):
    """Extract PERSON, ORGANIZATION, LOCATION entities with improved detection"""
    doc = nlp(text)
    entities = {'PERSON': [], 'ORGANIZATION': [], 'LOCATION': []}
    
    # First, get entities from spaCy
    for ent in doc.ents:
        label = ent.label_
        clean_name = clean_entity_name(ent.text)
        
        if clean_name:
            if label == 'PERSON':
                entities['PERSON'].append(clean_name)
            elif label in ['ORG', 'ORGANIZATION']:
                entities['ORGANIZATION'].append(clean_name)
            elif label in ['LOC', 'LOCATION', 'GPE']:
                entities['LOCATION'].append(clean_name)
    
    # Pattern matching for ALL CAPS organizations
    org_pattern = r'\b[A-Z][A-Z\s\-]+[A-Z]\b'
    potential_orgs = re.findall(org_pattern, text)
    
    for org in potential_orgs:
        org_clean = clean_entity_name(org)
        if org_clean and len(org_clean) > 2:
            if org_clean.lower() not in ['the', 'and', 'for', 'with', 'from', 'a', 'an', 'in', 'on', 'of']:
                if org_clean not in entities['ORGANIZATION']:
                    entities['ORGANIZATION'].append(org_clean)
    
    return entities

def process_ner(text: str) -> dict:
    """Process NER and return structured results matching frontend expectations"""
    entities = extract_entities(text)
    # Remove duplicates for counts
    unique_entities = {k: list(set(v)) for k, v in entities.items()}
    counts = {k: len(v) for k, v in unique_entities.items()}
    
    return {
        'entities': entities,  # Full list as frontend expects
        'counts': counts,
        'text': text
    }

def merge_related_entities(entities):
    """Merge related entities that might have been split (optional)"""
    orgs = entities['ORGANIZATION']
    merged_orgs = set(orgs)
    for org in list(orgs):
        if '-' in org:
            parts = org.split('-')
            for part in parts:
                if part in merged_orgs and part != org:
                    merged_orgs.discard(part)
    entities['ORGANIZATION'] = list(merged_orgs)
    return entities

def visualize_entities(entities):
    """Create bar chart visualization for interactive mode"""
    labels = ['PERSON', 'ORGANIZATION', 'LOCATION']
    counts = [len(set(entities.get(label, []))) for label in labels]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(count), ha='center', va='bottom', fontweight='bold')
    
    plt.title('Named Entity Recognition Results (SpaCy Transformer)', fontsize=14, fontweight='bold')
    plt.ylabel('Unique Entity Count', fontsize=12)
    plt.xlabel('Entity Types', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('spacy_plot.png', dpi=100)
    plt.show()

# Interactive CLI mode (existing)
print("="*60)
print("✅ SpaCy NER with Transformer Model")
print("="*60)

def interactive_mode():
    while True:
        user_input = input("\n\n📝 Enter text ('batch' for CSV, 'quit' to exit): ").strip()
        
        if user_input.lower() == 'quit':
            break
            
        if user_input.lower() == 'batch':
            csv_path = '../data/cleaned_data.csv'  # relative to q3/
            if not os.path.exists(csv_path):
                print(f"❌ Error: {csv_path} not found!")
                continue
                
            print(f"\n📊 Processing {csv_path}...")
            df = pd.read_csv(csv_path, nrows=500)
            
            df['person_count'] = 0
            df['org_count'] = 0
            df['loc_count'] = 0
            
            for idx, row in df.iterrows():
                if idx % 50 == 0:
                    print(f"   Processing row {idx}/{len(df)}...")
                text = str(row.get('text', ''))
                if text and text != 'nan':
                    ner_result = process_ner(text)
                    df.at[idx, 'person_count'] = ner_result['counts']['PERSON']
                    df.at[idx, 'org_count'] = ner_result['counts']['ORGANIZATION']
                    df.at[idx, 'loc_count'] = ner_result['counts']['LOCATION']
            
            output_file = 'ner_results.csv'
            df.to_csv(output_file, index=False)
            print(f"\n✅ Batch complete! Saved to {output_file}")
            continue
        
        # Single text
        if user_input:
            ner_result = process_ner(user_input)
            
            print("\n" + "="*60)
            print("EXTRACTED ENTITIES:")
            print("="*60)
            
            has_entities = False
            for entity_type, entity_list in ner_result['entities'].items():
                if entity_list:
                    has_entities = True
                    unique = sorted(set(entity_list))
                    print(f"\n{entity_type} ({ner_result['counts'][entity_type]}):")
                    for entity in unique[:10]:  # top 10
                        print(f"  • {entity}")
            
            if not has_entities:
                print("\nNo entities found.")
            
            print(f"\n📊 Total unique entities: {sum(ner_result['counts'].values())}")
            visualize_entities(ner_result['entities'])

# Programmatic JSON mode for frontend
if __name__ == "__main__":
    try:
        input_str = sys.stdin.read().strip()
        if not input_str:
            interactive_mode()
            sys.exit(0)
        
        data = json.loads(input_str)
        mode = data.get('mode')
        
        if mode == 'text':
            result = process_ner(data['text'])
            print(json.dumps(result, indent=None))
        elif mode == 'csv':
            file_path = data['file_path']
            if not os.path.exists(file_path):
                raise ValueError(f"CSV file not found: {file_path}")
            
            df = pd.read_csv(file_path)
            results = []
            for idx, row in df.head(100).iterrows():  # limit
                text = str(row.get('text', ''))
                if pd.notna(text) and text.strip():
                    ner = process_ner(text)
                    results.append({
                        'text': text[:100] + ('...' if len(text) > 100 else ''),
                        'counts': ner['counts']
                    })
            print(json.dumps({'results': results}, indent=None))
        else:
            raise ValueError(f"Unknown mode: {mode}")
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)

print("\n✅ NER processing complete!")
