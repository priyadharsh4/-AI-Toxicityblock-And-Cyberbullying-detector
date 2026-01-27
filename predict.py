import joblib
import re

model = joblib.load("model/toxic_model.pkl")

text = input("Enter your comment: ").strip()

if not text:
    print("❌ No input provided. Please enter a comment.")
    exit()

text_lower = text.lower()

labels = ['toxic', 'insult', 'threat', 'obscene', 'identity_hate']

label_names = {
    'toxic': 'Toxic',
    'insult': 'Insult',
    'threat': 'Threat',
    'obscene': 'Obscene',
    'identity_hate': 'Hate Speech'
}

thresholds = {
    'toxic': 0.90,
    'insult': 0.90,
    'obscene': 0.90,
    'threat': 0.90,
    'identity_hate': 0.90
}

# Rule vocabularies (VERY IMPORTANT)
obscene_words = ['fuck', 'fucking', 'shit', 'bitch', 'asshole']
threat_words = ['kill', 'murder', 'shoot', 'die', 'harm']
identity_words = ['religion', 'muslim', 'hindu', 'christian',
                  'black', 'white', 'women', 'men', 'caste', 'hate', 'hater']
insult_words = ['stupid', 'idiot', 'dumb', 'fool', 'asshole', 'loser']

# Safe/non-toxic phrases - whitelist
safe_phrases = ['i like u', 'i like you', 'i love', 'hello', 'hi', 'bye', 'thanks', 'please', 'ok', 'sure']

probs = model.predict_proba([text])
detected = []

# Check if input matches safe phrases - if so, return non-toxic
if any(safe_phrase in text_lower for safe_phrase in safe_phrases):
    detected = []
else:
    for i, label in enumerate(labels):
        if probs[i][0][1] >= thresholds[label]:

            # Obscene guard
            if label == 'obscene' and not any(w in text_lower for w in obscene_words):
                continue

            # Insult guard
            if label == 'insult' and not any(w in text_lower for w in insult_words):
                continue

            # Hate speech guard
            if label == 'identity_hate' and not any(w in text_lower for w in identity_words):
                continue

            # Threat guard
            if label == 'threat' and not any(w in text_lower for w in threat_words):
                continue

            detected.append(label_names[label])

if detected:
    print("⚠️ TOXIC COMMENT DETECTED")
    print("Detected Labels:", ", ".join(detected))
else:
    print("✅ NON-TOXIC COMMENT")
