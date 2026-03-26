import json
import re
import nltk
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import sys

def download_nltk_data():
    nltk_data_dir = os.path.expanduser('~/nltk_data')
    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)
    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.append(nltk_data_dir)
    
    required = ['punkt', 'stopwords', 'punkt_tab']
    for package in required:
        try:
            nltk.data.find(f'tokenizers/{package}' if 'punkt' in package else f'corpora/{package}')
        except LookupError:
            nltk.download(package, download_dir=nltk_data_dir)

print("Checking NLTK data...")
download_nltk_data()

try:
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import PorterStemmer
except ImportError:
    print("NLTK import error")
    sys.exit(1)

# Load intents from q4/intents.json
intents_path = 'intents.json'
with open(intents_path, 'r') as f:
    intents = json.load(f)

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

# TF-IDF setup
patterns = []
pattern_intents = []
for intent in intents:
    for pat in intent['patterns']:
        proc = preprocess(pat)
        if proc:
            patterns.append(proc)
            pattern_intents.append(intent['intent'])

vectorizer = TfidfVectorizer()
pattern_vecs = vectorizer.fit_transform(patterns) if patterns else None

def get_chatbot_response(message: str, conversation_history=None) -> dict:
    processed = preprocess(message)
    
    if not processed:
        return {
            'response': "Sorry, I didn't understand that.",
            'intent': 'unknown',
            'confidence': 0.0
        }
    
    if pattern_vecs is None:
        return {
            'response': "Chatbot setup error.",
            'intent': 'error',
            'confidence': 0.0
        }
    
    try:
        input_vec = vectorizer.transform([processed])
        sims = cosine_similarity(input_vec, pattern_vecs)[0]
        max_idx = np.argmax(sims)
        confidence = float(sims[max_idx])
        
        if confidence < 0.1:
            return {
                'response': "Not sure. Ask about NLP (NER, POS, sentiment) or AI apps. E.g. 'What is NER?'",
                'intent': 'unknown',
                'confidence': confidence
            }
        
        intent_key = pattern_intents[max_idx]
        for intent_obj in intents:
            if intent_obj['intent'] == intent_key:
                response = random.choice(intent_obj['responses'])
                return {
                    'response': response,
                    'intent': intent_key,
                    'confidence': confidence
                }
        
        return {
            'response': "What would you like to know about NLP?",
            'intent': 'default',
            'confidence': confidence
        }
    except Exception:
        return {
            'response': "Error occurred. Try again.",
            'intent': 'error',
            'confidence': 0.0
        }

# Interactive mode
def print_welcome():
    print("="*60)
    print("🤖 Q4 Chatbot (NLP/AI Assistant)")
    print("Ask about NER, POS, sentiment, AI apps...")
    print("="*60)

print_welcome()

conversation_history = []
while True:
    try:
        user_input = input("You: ").strip()
        if user_input.lower() in ['quit', 'bye', 'exit']:
            print("Bot: Bye! 👋")
            break
        
        if user_input:
            response = get_chatbot_response(user_input, conversation_history)
            print(f"Bot: {response['response']}")
            if response['intent'] != 'unknown':
                print(f"  (Intent: {response['intent']}, Conf: {response['confidence']:.2f})")
            conversation_history.append((user_input, response['response']))
    except KeyboardInterrupt:
        break

# Programmatic JSON mode
if __name__ == "__main__":
    try:
        input_str = sys.stdin.read().strip()
        if not input_str:
            # No input = interactive
            sys.exit(0)
        
        data = json.loads(input_str)
        result = get_chatbot_response(data.get('message', ''), data.get('history', []))
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({'response': str(e), 'intent': 'error', 'confidence': 0.0}), file=sys.stderr)
        sys.exit(1)
