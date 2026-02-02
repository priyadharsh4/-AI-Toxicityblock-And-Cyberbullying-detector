from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import time
import re

app = Flask(__name__)

# Load model (matches your train.py)
model = joblib.load("model/toxic_model.pkl")

# CORRECT LABELS (matches your train.py and CLI scripts)
labels = ['toxic', 'insult', 'threat', 'obscene', 'identity_hate']
label_names = {
    'toxic': 'Toxic',
    'insult': 'Insult', 
    'threat': 'Threat',
    'obscene': 'Obscene',
    'identity_hate': 'Hate Speech'
}

# Your exact thresholds from CLI scripts
thresholds = {
    'toxic': 0.90,
    'insult': 0.90,
    'obscene': 0.90,
    'threat': 0.90,
    'identity_hate': 0.90
}

# Your exact rule vocabularies
obscene_words = ['fuck', 'fucking', 'shit', 'bitch', 'asshole']
threat_words = ['kill', 'murder', 'shoot', 'die', 'harm']
identity_words = ['religion', 'muslim', 'hindu', 'christian', 'black', 'white', 'women', 'men', 'caste', 'hate', 'hater']
insult_words = ['stupid', 'idiot', 'dumb', 'fool', 'asshole', 'loser']

# Safe/non-toxic phrases - whitelist
safe_phrases = ['i like u', 'i like you', 'i love', 'hello', 'hi', 'bye', 'thanks', 'please', 'ok', 'sure']

# Safe words - exceptions to avoid false positives
safe_words = ['priya', 'dev', 'name', 'called']

def predict_toxic(text):
    """Exact same logic as your CLI scripts"""
    if not text or not text.strip():
        return []
    
    text_lower = text.lower().strip()
    
    # If text contains safe words only (no toxic keywords), return safe
    if any(word in text_lower for word in safe_words) and not any(w in text_lower for w in obscene_words + threat_words + identity_words):
        return []
    
    probs = model.predict_proba([text])
    detected = []
    
    # Check if input matches safe phrases - if so, return non-toxic
    if any(safe_phrase in text_lower for safe_phrase in safe_phrases):
        detected = []
    else:
        for i, label in enumerate(labels):
            if probs[i][0][1] >= thresholds[label]:  # probs[i] is array for label i, [0][1] is positive class prob
                # Apply your exact guards
                if label == 'obscene' and not any(w in text_lower for w in obscene_words):
                    continue
                if label == 'insult' and not any(w in text_lower for w in insult_words):
                    continue
                if label == 'threat' and not any(w in text_lower for w in threat_words):
                    continue
                if label == 'identity_hate' and not any(w in text_lower for w in identity_words):
                    continue
                detected.append(label_names[label])
    
    # Your semantic cleanup
    if 'Threat' in detected and 'Insult' in detected:
        detected.remove('Insult')
    
    return detected

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/api/detect', methods=['POST'])
def detect_toxicity():
    data = request.json
    text = data.get('text', '')
    
    # Load your model (use your existing variable name)
    prediction = model_pipeline.predict([text])[0]  # or 'model.predict' 
    is_toxic = int(prediction) == 1
    
    return jsonify({'toxic': bool(is_toxic)})
@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()
    data = request.json
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'Please enter text to analyze'}), 400
    
    # Use your exact prediction logic
    detected_labels = predict_toxic(text)
    status = 'toxic' if detected_labels else 'non-toxic'
    
    return jsonify({
        'status': status,
        'labels': detected_labels,
        'text': text,
        'confidence': 0.95 if status == 'toxic' else 0.05,  # Demo confidence
        'processing_time': round(time.time() - start_time, 2)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
