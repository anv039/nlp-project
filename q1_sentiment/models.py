import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, 
                             recall_score, f1_score,
                             confusion_matrix, classification_report)
from sklearn.utils.class_weight import compute_class_weight

# ── Load cleaned data ──────────────────────────────────────────────
df = pd.read_csv('data/cleaned_data.csv')
df = df.dropna(subset=['clean_text'])

X = df['clean_text']
y = df['sentiment']

# ── Train/Test Split (80/20) ───────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")

# ── Feature Extraction: TF-IDF ────────────────────────────────────
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf  = tfidf.transform(X_test)

# ── Handle Class Imbalance ────────────────────────────────────────
classes = np.unique(y_train)
weights = compute_class_weight('balanced', classes=classes, y=y_train)
class_weight_dict = dict(zip(classes, weights))
print(f"\nClass weights (to handle imbalance): {class_weight_dict}")

# ── Define 3 Models ───────────────────────────────────────────────
models = {
    'Naive Bayes'        : MultinomialNB(alpha=0.5),
    'SVM'                : LinearSVC(C=1.0, 
                                     class_weight='balanced', 
                                     max_iter=1000),
    'Logistic Regression': LogisticRegression(C=1.0, 
                                              class_weight='balanced',
                                              max_iter=1000,
                                              random_state=42)
}

# ── Train, Predict and Evaluate ───────────────────────────────────
results = {}

for name, model in models.items():
    print(f"\n{'='*50}")
    print(f"Training: {name}")
    model.fit(X_train_tfidf, y_train)
    y_pred = model.predict(X_test_tfidf)
    
    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted')
    rec  = recall_score(y_test, y_pred, average='weighted')
    f1   = f1_score(y_test, y_pred, average='weighted')
    
    results[name] = {
        'Accuracy' : round(acc*100, 2),
        'Precision': round(prec*100, 2),
        'Recall'   : round(rec*100, 2),
        'F1 Score' : round(f1*100, 2)
    }
    
    print(f"Accuracy : {acc*100:.2f}%")
    print(f"Precision: {prec*100:.2f}%")
    print(f"Recall   : {rec*100:.2f}%")
    print(f"F1 Score : {f1*100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

# ── Results Comparison Table ──────────────────────────────────────
print("\n" + "="*50)
print("FINAL RESULTS COMPARISON TABLE")
print("="*50)
results_df = pd.DataFrame(results).T
print(results_df)
results_df.to_csv('q1_sentiment/results.csv')

# ── Plot 1: Confusion Matrices ────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, (name, model) in zip(axes, models.items()):
    y_pred = model.predict(X_test_tfidf)
    cm = confusion_matrix(y_test, y_pred, 
                          labels=['positive','negative','neutral'])
    sns.heatmap(cm, annot=True, fmt='d', ax=ax,
                xticklabels=['pos','neg','neu'],
                yticklabels=['pos','neg','neu'],
                cmap='Blues')
    ax.set_title(f'{name}')
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')

plt.suptitle('Confusion Matrices - All 3 Models', fontsize=14)
plt.tight_layout()
plt.savefig('q1_sentiment/confusion_matrices.png', dpi=150)
plt.show()
print("Confusion matrices saved.")

# ── Plot 2: F1 Score Comparison Bar Chart ─────────────────────────
plt.figure(figsize=(8, 5))
metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
x = np.arange(len(metrics))
width = 0.25

for i, (name, scores) in enumerate(results.items()):
    vals = [scores[m] for m in metrics]
    plt.bar(x + i*width, vals, width, label=name)

plt.xlabel('Metric')
plt.ylabel('Score (%)')
plt.title('Model Comparison - All Metrics')
plt.xticks(x + width, metrics)
plt.legend()
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig('q1_sentiment/model_comparison.png', dpi=150)
plt.show()
print("Model comparison chart saved.")