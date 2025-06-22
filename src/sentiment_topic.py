import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from transformers import pipeline
from cleaning_text import preprocess_dataframe

from fastopic import FASTopic
from topmost import Preprocess
import numpy as np
import torch

# ✅ Simple whitespace tokenizer
def whitespace_tokenizer(text):
    return text.split()

# ✅ Check if CUDA is available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"✅ FASTopic will use: {DEVICE}")

# ✅ Indonesian sentiment model
sentiment_model = pipeline(
    "sentiment-analysis",
    model="w11wo/indonesian-roberta-base-sentiment-classifier",
    tokenizer="w11wo/indonesian-roberta-base-sentiment-classifier"
)

def analyze_sentiment(df, text_column="Cleaned_Tweet", output_path=None):
    texts = df[text_column].astype(str).tolist()
    results = sentiment_model(texts, batch_size=32)
    df["Sentiment"] = [r["label"] for r in results]
    if output_path:
        df.to_csv(output_path, index=False)
        print(f"📁 Sentiment saved to {output_path}")
    return df

def generate_wordcloud(df, text_column="Cleaned_Tweet", sentiment_column=None, output_image_path=None):
    if sentiment_column:
        sentiments = df[sentiment_column].dropna().unique()
        n_panels = len(sentiments) + 1
        plt.figure(figsize=(5 * n_panels, 5))

        all_text = " ".join(df[text_column].astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
        plt.subplot(1, n_panels, 1)
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title("All")

        for idx, sentiment in enumerate(sentiments, start=2):
            subset = df[df[sentiment_column] == sentiment]
            subset_text = " ".join(subset[text_column].astype(str))
            wc = WordCloud(width=800, height=400, background_color='white').generate(subset_text)
            plt.subplot(1, n_panels, idx)
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            plt.title(sentiment.capitalize())

        plt.tight_layout()
        if output_image_path:
            plt.savefig(output_image_path)
            print(f"🖼️ Wordcloud (all + per sentiment) saved to {output_image_path}")
        plt.close()
    else:
        all_text = " ".join(df[text_column].astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title("All")
        plt.tight_layout()
        if output_image_path:
            plt.savefig(output_image_path)
            print(f"🖼️ Wordcloud saved to {output_image_path}")
        plt.close()

def extract_topics_per_sentiment(
    df,
    text_column="Cleaned_Tweet",
    sentiment_column="Sentiment",
    output_prefix="output_analysis/topics",
    ts=""
):
    topic_models = {}
    sentiments = df[sentiment_column].dropna().unique()

    if len(sentiments) == 0:
        print("⚠️ Tidak ada data sentimen tersedia untuk topic modeling.")
        return topic_models

    for sentiment in sentiments:
        subset = df[df[sentiment_column] == sentiment].copy()
        print(f"🔍 Modeling topic for sentiment: {sentiment} ({len(subset)} tweets)")

        if subset.empty:
            print(f"⚠️ Tidak ada data untuk sentimen '{sentiment}', dilewati.")
            continue

        try:
            preprocess_module = Preprocess(
                vocab_size=10000,
                tokenizer=whitespace_tokenizer
            )

            # Try CUDA first, fallback to CPU if memory error occurs
            try:
                model = FASTopic(
                    num_topics=5,
                    preprocess=preprocess_module,
                    doc_embed_model="paraphrase-multilingual-MiniLM-L12-v2",
                    device=DEVICE,
                    verbose=True
                )
                texts = subset[text_column].astype(str).tolist()
                top_words, theta = model.fit_transform(texts)

            except RuntimeError as e:
                if "CUDA out of memory" in str(e):
                    print("⚠️ CUDA memory error, switching to CPU...")
                    model = FASTopic(
                        num_topics=5,
                        preprocess=preprocess_module,
                        doc_embed_model="paraphrase-multilingual-MiniLM-L12-v2",
                        device="cpu",
                        verbose=True
                    )
                    top_words, theta = model.fit_transform(subset[text_column].astype(str).tolist())
                else:
                    raise e

            subset["Topic"] = np.argmax(theta, axis=1)

            # Save result
            csv_path = f"{output_prefix}_{sentiment.lower()}_{ts}.csv"
            subset.to_csv(csv_path, index=False)
            print(f"📁 Topics saved to {csv_path}")

            topic_models[sentiment] = model

        except Exception as e:
            print(f"❌ Gagal membuat topik untuk sentimen '{sentiment}': {e}")
            continue

    return topic_models
