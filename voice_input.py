import joblib
import speech_recognition as sr
import os

# Load trained model
model = joblib.load("model/toxic_model.pkl")

labels = ['toxic', 'insult', 'threat', 'obscene', 'identity_hate']

label_names = {
    'toxic': 'Toxic',
    'insult': 'Insult',
    'threat': 'Threat',
    'obscene': 'Obscene',
    'identity_hate': 'Hate Speech'
}

# Label-wise thresholds
thresholds = {
    'toxic': 0.30,
    'insult': 0.45,
    'obscene': 0.65,
    'threat': 0.70,
    'identity_hate': 0.80
}

# Rule vocabularies (filters only)
obscene_words = ['fuck', 'fucking', 'shit', 'bitch', 'asshole']
threat_words = ['kill', 'murder', 'shoot', 'die', 'harm']
identity_words = [
    'muslim', 'hindu', 'christian', 'black', 'white',
    'women', 'men', 'caste', 'religion'
]

def predict_text(text):
    text_lower = text.lower()
    probs = model.predict_proba([text])
    detected = []

    for i, label in enumerate(labels):
        if probs[i][0][1] >= thresholds[label]:

            if label == 'obscene' and not any(w in text_lower for w in obscene_words):
                continue

            if label == 'threat' and not any(w in text_lower for w in threat_words):
                continue

            if label == 'identity_hate' and not any(w in text_lower for w in identity_words):
                continue

            detected.append(label_names[label])

    return detected


def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙 Speak now...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return None
    except sr.RequestError:
        print("❌ Speech service unavailable")
        return None


def file_input(file_path):
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return None
    except sr.RequestError:
        print("❌ Speech service unavailable")
        return None


# -------- MAIN MENU --------
print("Choose input method:")
print("1. Voice input (microphone)")
print("2. Audio file upload (.wav)")

choice = input("Enter choice (1 or 2): ").strip()

recognized_text = None

if choice == '1':
    recognized_text = voice_input()

elif choice == '2':
    file_path = input("Enter audio file path (.wav): ").strip()
    if not os.path.exists(file_path):
        print("❌ File not found")
        exit()
    recognized_text = file_input(file_path)

else:
    print("❌ Invalid choice")
    exit()

if not recognized_text:
    exit()

# Show recognized text
print("\n📝 Recognized Text:")
print(recognized_text)

# Prediction
detected_labels = predict_text(recognized_text)

# ---- Semantic cleanup ----
if 'Threat' in detected_labels and 'Insult' in detected_labels:
    detected_labels.remove('Insult')

if detected_labels:
    print("\n⚠️ TOXIC COMMENT DETECTED")
    print("Detected Labels:", ", ".join(detected_labels))
else:
    print("\n✅ NON-TOXIC COMMENT")

