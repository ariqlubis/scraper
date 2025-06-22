# src/cleaning_text.py

import re
import string
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

factory_stopwords = StopWordRemoverFactory()
stopwords = set(factory_stopwords.get_stop_words())
stemmer = StemmerFactory().create_stemmer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|@\w+|#\w+", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def remove_stopwords(text):
    return " ".join([word for word in text.split() if word not in stopwords])

def stem_text(text):
    return stemmer.stem(text)

def preprocess(text):
    text = clean_text(text)
    text = remove_stopwords(text)
    text = stem_text(text)
    return text

def preprocess_dataframe(df, text_column="Tweet"):
    df["Cleaned_Tweet"] = df[text_column].astype(str).apply(preprocess)
    return df
