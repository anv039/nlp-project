import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity

# ── Load GloVe embeddings ──────────────────────────────────────────
print("Loading GloVe embeddings... (this takes ~30 seconds)")
embeddings = {}
with open('data/glove.6B.100d.txt', 'r', encoding='utf-8') as f:
    for line in f:
        values = line.split()
        word   = values[0]
        vector = np.array(values[1:], dtype='float32')
        embeddings[word] = vector

print(f"Loaded {len(embeddings):,} word vectors")

# ── Cosine Similarity Function ─────────────────────────────────────
def get_similarity(word1, word2):
    if word1 not in embeddings:
        return f"'{word1}' not found in vocabulary"
    if word2 not in embeddings:
        return f"'{word2}' not found in vocabulary"
    v1 = embeddings[word1].reshape(1, -1)
    v2 = embeddings[word2].reshape(1, -1)
    score = cosine_similarity(v1, v2)[0][0]
    return round(float(score), 4)

# ── Required Word Pairs from Q2 ───────────────────────────────────
pairs = [
    ('king',    'queen'),
    ('doctor',  'nurse'),
    ('car',     'tree'),
]

print("\n" + "="*50)
print("COSINE SIMILARITY RESULTS")
print("="*50)
results = []
for w1, w2 in pairs:
    score = get_similarity(w1, w2)
    results.append({'Word 1': w1, 'Word 2': w2, 'Cosine Similarity': score})
    print(f"{w1:10} <-> {w2:10} : {score}")

# ── Bonus: Extra interesting pairs ───────────────────────────────
bonus_pairs = [
    ('man',     'woman'),
    ('paris',   'france'),
    ('happy',   'sad'),
    ('bitcoin', 'stock'),
]
print("\nBonus pairs:")
for w1, w2 in bonus_pairs:
    score = get_similarity(w1, w2)
    results.append({'Word 1': w1, 'Word 2': w2, 'Cosine Similarity': score})
    print(f"{w1:10} <-> {w2:10} : {score}")

# ── Plot 1: Bar chart of similarities ─────────────────────────────
labels = [f"{r['Word 1']} / {r['Word 2']}" for r in results]
scores = [r['Cosine Similarity'] for r in results]
colors = ['#2ecc71' if s > 0.5 else '#e74c3c' if s < 0.2 else '#3498db' 
          for s in scores]

plt.figure(figsize=(10, 5))
bars = plt.barh(labels, scores, color=colors)
plt.xlabel('Cosine Similarity Score')
plt.title('Word Embedding Cosine Similarity (GloVe 100d)')
plt.xlim(0, 1)
for bar, score in zip(bars, scores):
    plt.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
             f'{score:.4f}', va='center', fontsize=10)
plt.tight_layout()
plt.savefig('q2_embeddings/similarity_scores.png', dpi=150)
plt.show()
print("\nSimilarity bar chart saved.")

# ── Plot 2: Heatmap of word vectors (first 10 dims) ───────────────
words_to_plot = ['king', 'queen', 'doctor', 'nurse', 'car', 'tree']
matrix = np.array([embeddings[w][:20] for w in words_to_plot])

plt.figure(figsize=(14, 4))
sns.heatmap(matrix, xticklabels=[f'd{i}' for i in range(20)],
            yticklabels=words_to_plot, cmap='coolwarm', center=0)
plt.title('GloVe Word Vectors — First 20 Dimensions')
plt.tight_layout()
plt.savefig('q2_embeddings/vector_heatmap.png', dpi=150)
plt.show()
print("Vector heatmap saved.")