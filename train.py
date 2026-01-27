from sklearn.multioutput import MultiOutputClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd
import joblib
import os

data = pd.read_csv("dataset/train.csv")

X = data['comment_text']
y = data[['toxic', 'insult', 'threat', 'obscene', 'identity_hate']]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = Pipeline([
    ('tfidf', TfidfVectorizer(
        stop_words='english',
        max_features=8000,
        analyzer='char_wb',
        ngram_range=(3, 5)
    )),
    ('clf', MultiOutputClassifier(
        LogisticRegression(
            max_iter=1000,
            solver='liblinear',
            class_weight='balanced'
        )
    ))
])

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=y.columns))

os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/toxic_model.pkl")
