import json
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import random
from typing import List, Dict

# NLTK setup
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Load intents
intents_path = os.path.join(os.path.dirname(__file__), 'intents.json')
if not os.path.exists(intents_path):
    intents_path = 'q4/intents.json'

with open(intents_path, 'r') as f:
    intents = json.load(f)

# Preprocess
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def preprocess(text):
    text = text.lower()
    try:
        tokens = word_tokenize(text)
    except:
        return ""
    tokens = [stemmer.stem(w) for w in tokens if w.isalpha() and w not in stop_words]
    return ' '.join(tokens)

# Prepare TF-IDF
patterns = []
pattern_intents = []
for intent in intents:
    for pat in intent['patterns']:
        processed_pat = preprocess(pat)
        if processed_pat:
            patterns.append(processed_pat)
            pattern_intents.append(intent['intent'])

vectorizer = TfidfVectorizer()
if patterns:
    pattern_vecs = vectorizer.fit_transform(patterns)

def get_chatbot_response(message: str, conversation_history: List[Dict[str, str]] = None) -> dict:
    """Get chatbot response for user message"""
    processed = preprocess(message)
    
    if not processed:
        return {
            'response': "Sorry, I didn't understand that. Could you please rephrase?",
            'intent': 'unknown',
            'confidence': 0.0
        }
    
    try:
        input_vec = vectorizer.transform([processed])
        sims = cosine_similarity(input_vec, pattern_vecs)[0]
        max_idx = np.argmax(sims)
        confidence = float(sims[max_idx])
        
        if confidence < 0.1:
            return {
                'response': "I'm not sure about that. I can answer questions about NLP concepts (NER, POS, sentiment) or AI applications. Try asking: 'What is NER?' or 'Tell me about chatbots'",
                'intent': 'unknown',
                'confidence': confidence
            }
        
        intent = pattern_intents[max_idx]
        
        # Find response for intent
        for intent_obj in intents:
            if intent_obj['intent'] == intent:
                response = random.choice(intent_obj['responses'])
                return {
                    'response': response,
                    'intent': intent,
                    'confidence': confidence
                }
        
        return {
            'response': "I can answer about NLP concepts or AI applications. What would you like to know?",
            'intent': 'default',
            'confidence': confidence
        }
    
    except Exception as e:
        return {
            'response': "Sorry, I encountered an error. Please try again.",
            'intent': 'error',
            'confidence': 0.0
        }