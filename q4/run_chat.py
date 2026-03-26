import sys
import json
import re
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Skip NLTK - use simple split for tokenization
def simple_tokenize(text):
    return re.findall(r'\b[a-zA-Z]+\b', text.lower())

def preprocess(text):
    tokens = simple_tokenize(text)
    stop_words = {'the', 'is', 'in', 'at', 'of', 'to', 'a', 'an', 'and', 'or', 'for', 'on', 'with', 'as'}
    tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
    return ' '.join(tokens)

# Intents (hardcoded for reliability)
intents = [
  {"intent": "greeting", "patterns": ["hi", "hello", "hey"], "responses": ["Hi! Ask about NLP concepts like NER, POS, sentiment analysis!" ]},
  {"intent": "ner", "patterns": ["ner", "named entity", "entity recognition"], "responses": ["NER identifies PERSON, ORGANIZATION, LOCATION in text using SpaCy transformer model."]},
  {"intent": "pos", "patterns": ["pos", "part of speech"], "responses": ["POS tagging labels words as noun, verb, adj - e.g. 'running' as VBG."]},
  {"intent": "sentiment", "patterns": ["sentiment", "sentiment analysis"], "responses": ["Sentiment Analysis: positive/neutral/negative - perfect for stock headlines!"]},
  {"intent": "chatbot", "patterns": ["chatbot", "chatbots"], "responses": ["Chatbots use TF-IDF intent matching like this demo, or advanced LLMs."]},
  {"intent": "unknown", "patterns": [""], "responses": ["Try 'what is NER?', 'explain POS', 'sentiment analysis'"]},
]

print("✅ Hardcoded 6 intents ready", file=sys.stderr)

# Build TF-IDF
patterns = []
pattern_intents = []
for intent in intents:
    for pat in intent['patterns']:
        proc = preprocess(pat)
        patterns.append(proc)
        pattern_intents.append(intent['intent'])

vectorizer = TfidfVectorizer()
pattern_vecs = vectorizer.fit_transform(patterns)

def get_response(message):
    proc_msg = preprocess(message)
    input_vec = vectorizer.transform([proc_msg])
    sims = cosine_similarity(input_vec, pattern_vecs)[0]
    
    max_sim = np.max(sims)
    best_idx = np.argmax(sims)
    
    intent = pattern_intents[best_idx]
    
    if max_sim < 0.1:
        intent = "unknown"
    
    for i_obj in intents:
        if i_obj["intent"] == intent:
            resp = random.choice(i_obj["responses"])
            return {"response": resp, "intent": intent, "confidence": float(max_sim)}
    
    return {"response": "NLP expert here! Ask about NER or sentiment analysis.", "intent": "default", "confidence": 0.0}

if __name__ == "__main__":
    try:
        data = json.loads(sys.stdin.read().strip())
        msg = data.get('message', 'hi')
        result = get_response(msg)
        print(json.dumps(result))
        print("✅ Processed:", msg, file=sys.stderr)
    except Exception as e:
        print(json.dumps({"response": "Error processing. Try again.", "intent": "error", "confidence": 0.0}))
        print("ERROR:", str(e), file=sys.stderr)

