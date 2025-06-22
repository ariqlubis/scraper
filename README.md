# 🐦 Twitter Scraper + Sentiment & Topic Analysis (Indonesian)

Crawl Twitter using Selenium, analyze Indonesian sentiment with HuggingFace, and extract topics using FASTopic.

---

## 🚀 Features

- ✅ Scrape Twitter/X using Selenium (no API)
- ✅ Keyword search with custom date range
- ✅ Sentiment analysis using a RoBERTa Indonesian model
- ✅ Topic modeling with multilingual embeddings via FASTopic
- ✅ Wordcloud generation per sentiment
- ✅ CPU or GPU (CUDA) supported
- ✅ Outputs in CSV, JSON, or Excel

---

## ⚙️ Requirements

- Python 3.10+
- Google Chrome (latest)
- ChromeDriver matching your Chrome version
- [Astral CLI + uv](https://astral.sh/docs/getting-started/)

---

## ⚡ Setup with Astral + uv (Windows)

### 1. Install Astral CLI

```bash
pip install astral-cli
```

### 2. Initialize the Astral project

```bash
astral init --yes
```

### 3. Install dependencies using uv

```bash
uv pip install -r requirements.txt
```

### 4. Create `.env` file for login

Create a file named `.env` in the project root:

```env
TWITTER_USER=your_username
TWITTER_PASS=your_password
```

> ❗ Twitter 2FA is not supported.

---

## 🔧 Configure `config.py`

Update keywords and options:

```python
KEYWORDS = ["Youtube", "Perang"]
SINCE = "2025-06-01"
UNTIL = "2025-06-22"
LANGUAGE = "Id"
OUTPUT_FORMAT = "csv"  # or "json", "excel"
HEADLESS = False       # Set to True to hide Chrome
```

Make sure you have `chromedriver.exe` for your Chrome version:  
➡️ https://chromedriver.chromium.org/downloads

---

## 🧹 Step 1: Run the Scraper

```bash
uv python src/x_scraper.py
```

✅ Output: `output/twitter_data_YYYYMMDD_HHMMSS.csv`

---

## 📊 Step 2: Run the Analysis Pipeline

```bash
uv python src/main.py
```

✅ Outputs saved to `output_analysis/`:

- Cleaned data CSV
- Sentiment-labeled tweets
- Wordcloud image (PNG)
- Topics per sentiment (CSV)

---

## 🧠 Models Used

- **Sentiment Analysis**:  
  [`w11wo/indonesian-roberta-base-sentiment-classifier`](https://huggingface.co/w11wo/indonesian-roberta-base-sentiment-classifier)

- **Topic Modeling**:  
  `FASTopic` + `paraphrase-multilingual-MiniLM-L12-v2`

✅ Works on CPU and GPU (auto fallback if CUDA is full)

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| **CUDA out of memory** | The script switches to CPU automatically |
| **Twitter login fails** | Double-check `.env` credentials (2FA not supported) |
| **ChromeDriver error** | Download version that matches your Chrome |

---

## 📂 Project Structure

```
scraper/
├── src/
│   ├── x_scraper.py           # Scrapes tweets
│   ├── main.py                # Runs full analysis
│   ├── sentiment_topic.py     # Sentiment & topic functions
│   └── cleaning_text.py       # Text preprocessing
├── output/                    # Raw tweet data
├── output_analysis/           # Cleaned data, sentiment, topics
├── config.py
├── .env                       # Twitter login credentials
├── requirements.txt
└── README.md
```

---

## 📬 Sample Output (sentiment + topic)

| Username | Tweet | Sentiment | Topic |
|----------|-------|-----------|--------|
| @user123 | "Acaranya seru banget!" | positive | 1 |
| @user456 | "ATM bermasalah." | negative | 4 |

---

## 👨‍💻 Author

Made with ❤️ by [@ariqlubis](https://github.com/ariqlubis)

---

## 📜 License

MIT — Use, share, and modify freely.
