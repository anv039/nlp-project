import sys
import json
import spacy
import re

# Inline ner_processor logic (self-contained)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print(json.dumps({'error': 'spaCy model not found'}))
    sys.exit(1)

def clean_entity_name(name):
    name = ' '.join(name.split())
    if name == '-' or name.startswith('-') or name.endswith('-'):
        return None
    return name

def process_ner(text: str) -> dict:
    doc = nlp(text)
    entities = {'PERSON': [], 'ORGANIZATION': [], 'LOCATION': []}
    seen = set()
    for ent in doc.ents:
        clean = clean_entity_name(ent.text)
        if clean and clean not in seen:
            seen.add(clean)
            label = ent.label_
            if label == 'PERSON':
                entities['PERSON'].append(clean)
            elif label in ['ORG', 'ORGANIZATION']:
                entities['ORGANIZATION'].append(clean)
            elif label in ['LOC', 'GPE', 'LOCATION']:
                entities['LOCATION'].append(clean)
    
    # ALL CAPS ORG pattern
    org_pattern = r'\b[A-Z][A-Z\s\-]+[A-Z]\b'
    for org in re.findall(org_pattern, text):
        clean = clean_entity_name(org)
        if clean and len(clean) > 2 and clean.lower() not in ['the', 'and', 'for']:
            if clean not in entities['ORGANIZATION']:
                entities['ORGANIZATION'].append(clean)
    
    counts = {k: len(set(v)) for k, v in entities.items()}
    return {'entities': entities, 'counts': counts, 'text': text}

if __name__ == "__main__":
    try:
        data = json.loads(sys.stdin.read().strip())
        mode = data.get('mode', 'text')
        if mode == 'text':
            print(json.dumps(process_ner(data['text'])))
        else:
            print(json.dumps({'error': f'Unsupported mode: {mode}'}))
    except Exception as e:
        print(json.dumps({'error': str(e)}))

