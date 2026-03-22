import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, validation_curve
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

# ── Load data ──────────────────────────────────────────────────────
df = pd.read_csv('data/cleaned_data.csv').dropna(subset=['clean_text'])
X = df['clean_text']
y = df['sentiment']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf  = tfidf.transform(X_test)

# ── Plot 1: Naive Bayes - alpha hyperparameter curve ──────────────
print("Generating Naive Bayes validation curve...")
alpha_range = [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]

train_scores, val_scores = validation_curve(
    MultinomialNB(), X_train_tfidf, y_train,
    param_name='alpha', param_range=alpha_range,
    cv=5, scoring='f1_weighted', n_jobs=-1)

train_mean = np.mean(train_scores, axis=1) * 100
val_mean   = np.mean(val_scores,   axis=1) * 100

plt.figure(figsize=(8, 5))
plt.plot(alpha_range, train_mean, 'o-', label='Training F1',   color='#2ecc71')
plt.plot(alpha_range, val_mean,   's-', label='Validation F1', color='#e74c3c')
plt.xscale('log')
plt.xlabel('Alpha (smoothing parameter)')
plt.ylabel('F1 Score (%)')
plt.title('Naive Bayes — Hyperparameter Tuning (Alpha)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('q1_sentiment/nb_validation_curve.png', dpi=150)
plt.show()
print("Naive Bayes curve saved.")

# ── Plot 2: SVM - C hyperparameter curve ─────────────────────────
print("Generating SVM validation curve...")
C_range = [0.001, 0.01, 0.1, 1.0, 10.0]

train_scores_svm, val_scores_svm = validation_curve(
    LinearSVC(class_weight='balanced', max_iter=2000),
    X_train_tfidf, y_train,
    param_name='C', param_range=C_range,
    cv=5, scoring='f1_weighted', n_jobs=-1)

train_mean_svm = np.mean(train_scores_svm, axis=1) * 100
val_mean_svm   = np.mean(val_scores_svm,   axis=1) * 100

plt.figure(figsize=(8, 5))
plt.plot(C_range, train_mean_svm, 'o-', label='Training F1',   color='#3498db')
plt.plot(C_range, val_mean_svm,   's-', label='Validation F1', color='#e74c3c')
plt.xscale('log')
plt.xlabel('C (regularization parameter)')
plt.ylabel('F1 Score (%)')
plt.title('SVM — Hyperparameter Tuning (C)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('q1_sentiment/svm_validation_curve.png', dpi=150)
plt.show()
print("SVM curve saved.")

# ── Hyperparameter Summary Table ──────────────────────────────────
print("\n" + "="*50)
print("HYPERPARAMETER SUMMARY")
print("="*50)
summary = pd.DataFrame({
    'Model'            : ['Naive Bayes', 'SVM', 'Logistic Regression'],
    'Key Hyperparameter': ['alpha=0.5', 'C=1.0', 'C=1.0'],
    'Class Weight'     : ['None', 'balanced', 'balanced'],
    'Max Features'     : ['5000 (TF-IDF)', '5000 (TF-IDF)', '5000 (TF-IDF)'],
    'ngram_range'      : ['(1,2)', '(1,2)', '(1,2)']
})
print(summary.to_string(index=False))
summary.to_csv('q1_sentiment/hyperparameters.csv', index=False)
print("\nHyperparameter table saved.")