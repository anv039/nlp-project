import spacy
import re
from typing import Dict, List

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_trf")
except:
    import os
    os.system("python -m spacy download en_core_web_trf")
    nlp = spacy.load("en_core_web_trf")

def clean_entity_name(name):
    """Clean up entity names"""
    name = ' '.join(name.split())
    if name == '-' or name.startswith('-') or name.endswith('-'):
        return None
    return name

def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract PERSON, ORGANIZATION, LOCATION entities"""
    doc = nlp(text)
    entities = {'PERSON': [], 'ORGANIZATION': [], 'LOCATION': []}
    seen_entities = set()
    
    for ent in doc.ents:
        label = ent.label_
        clean_name = clean_entity_name(ent.text)
        
        if clean_name and clean_name not in seen_entities:
            seen_entities.add(clean_name)
            
            if label == 'PERSON':
                entities['PERSON'].append(clean_name)
            elif label in ['ORG', 'ORGANIZATION']:
                entities['ORGANIZATION'].append(clean_name)
            elif label in ['LOC', 'LOCATION', 'GPE']:
                if clean_name not in entities['ORGANIZATION']:
                    entities['LOCATION'].append(clean_name)
    
    # Pattern matching for ALL CAPS organizations
    org_pattern = r'\b[A-Z][A-Z\s\-]+[A-Z]\b'
    potential_orgs = re.findall(org_pattern, text)
    
    for org in potential_orgs:
        org_clean = clean_entity_name(org)
        if org_clean and len(org_clean) > 2:
            if org_clean.lower() not in ['the', 'and', 'for', 'with', 'from']:
                if org_clean not in entities['ORGANIZATION'] and org_clean not in seen_entities:
                    entities['ORGANIZATION'].append(org_clean)
    
    return entities

def process_ner(text: str) -> dict:
    """Process NER and return structured results"""
    entities = extract_entities(text)
    counts = {k: len(set(v)) for k, v in entities.items()}
    
    return {
        'entities': entities,
        'counts': counts,
        'text': text
    }