# src/main.py

import os
import pandas as pd
from datetime import datetime
from glob import glob

from cleaning_text import preprocess_dataframe
from sentiment_topic import (
    analyze_sentiment,
    generate_wordcloud,
    extract_topics_per_sentiment
)

# Cari file terbaru dari output/
latest_file = max(glob("output/twitter_data_*.csv"), key=os.path.getctime)
df = pd.read_csv(latest_file)
print(f"📄 Loaded: {latest_file}")

# Setup
os.makedirs("output_analysis", exist_ok=True)
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

# Step 1: Preprocessing
df_cleaned = preprocess_dataframe(df)
cleaned_path = f"output_analysis/cleaned_{ts}.csv"
df_cleaned.to_csv(cleaned_path, index=False)
print(f"📁 Cleaned tweet saved to {cleaned_path}")

# Step 2: Sentiment analysis
sentiment_path = f"output_analysis/sentiment_{ts}.csv"
df_sentiment = analyze_sentiment(df_cleaned, output_path=sentiment_path)

# Step 3: WordCloud
wordcloud_path = f"output_analysis/wordcloud_{ts}.png"
generate_wordcloud(
    df_sentiment,
    text_column="Cleaned_Tweet",
    sentiment_column="Sentiment",
    output_image_path=wordcloud_path
)

# Step 4: Topic modeling per sentiment
extract_topics_per_sentiment(
    df_sentiment,
    text_column="Cleaned_Tweet",
    sentiment_column="Sentiment",
    output_prefix="output_analysis/topics",
    ts=ts
)
