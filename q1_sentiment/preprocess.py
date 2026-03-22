import pandas as pd
import nltk
import re
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from wordcloud import WordCloud

# Load dataset
df = pd.read_csv('data/all-data.csv',
                 encoding='latin-1',
                 header=None,
                 names=['sentiment', 'text'])

# Initialize tools
stop_words = set(stopwords.words('english'))
# Keep these financial words even if they are stopwords
financial_keep = {'up', 'down', 'no', 'not', 'above', 'below', 'against'}
stop_words = stop_words - financial_keep
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    # Lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords and lemmatize
    tokens = [lemmatizer.lemmatize(t) for t in tokens 
              if t not in stop_words and len(t) > 2]
    return ' '.join(tokens)

# Apply preprocessing
print("Preprocessing text...")
df['clean_text'] = df['text'].apply(preprocess)

# Show before and after
print("\nOriginal:", df['text'][0])
print("\nCleaned: ", df['clean_text'][0])

# Save cleaned data
df.to_csv('data/cleaned_data.csv', index=False)
print("\nCleaned data saved to data/cleaned_data.csv")
print("Shape:", df.shape)

# Plot 1 - Class distribution
plt.figure(figsize=(7, 4))
sns.countplot(x='sentiment', data=df, 
              palette={'positive':'#2ecc71', 
                       'negative':'#e74c3c', 
                       'neutral':'#3498db'})
plt.title('Sentiment Class Distribution')
plt.xlabel('Sentiment')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig('q1_sentiment/class_distribution.png', dpi=150)
plt.show()
print("Class distribution chart saved.")

# Plot 2 - Wordcloud per sentiment
for sentiment in ['positive', 'negative', 'neutral']:
    text = ' '.join(df[df['sentiment'] == sentiment]['clean_text'])
    wc = WordCloud(width=800, height=400, 
                   background_color='white').generate(text)
    plt.figure(figsize=(8, 4))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Word Cloud - {sentiment.capitalize()}')
    plt.tight_layout()
    plt.savefig(f'q1_sentiment/wordcloud_{sentiment}.png', dpi=150)
    plt.show()
    print(f"Wordcloud saved for {sentiment}")