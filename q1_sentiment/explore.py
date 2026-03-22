import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv('data/all-data.csv', 
                 encoding='latin-1', 
                 header=None, 
                 names=['sentiment', 'text'])

# Basic exploration
print("Shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())
print("\nSentiment distribution:")
print(df['sentiment'].value_counts())
print("\nMissing values:")
print(df.isnull().sum())