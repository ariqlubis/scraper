import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from datetime import datetime
import re
from config import *

print("Hi, Salma")

load_dotenv()
USERNAME = os.getenv("TWITTER_USER")
PASSWORD = os.getenv("TWITTER_PASS")

# Setup browser, Salma
options = webdriver.ChromeOptions()
if HEADLESS:
    options.add_argument("--headless")
if MAXIMIZED:
    options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
wait = WebDriverWait(driver, 15)

def login():
    try:
        driver.get("https://twitter.com/i/flow/login")
        
        # Username
        username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
        username_input.send_keys(USERNAME)
        
        # Click Next
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]/..')))
        next_button.click()
        time.sleep(2)
        
        # Password
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
        password_input.send_keys(PASSWORD)
        
        # Login button
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Log in"]/..')))
        login_button.click()
        time.sleep(5)
        
        print("✅ Login berhasil!")
    except Exception as e:
        print(f"❌ Login gagal: {e}")

def scroll_down():
    driver.execute_script("window.scrollBy(0, 1000)")
    time.sleep(SCROLL_DELAY)

def parse_tweets():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup.find_all("article", {"data-testid": "tweet"})

def extract_engagement_stats(tweet_element):
    """Extract like, retweet, reply, views counts with multiple fallback methods"""
    stats = {"Reply": "0", "Retweet": "0", "Like": "0", "Views": "0"}
    
    try:
        reply_elem = tweet_element.find('div', {'data-testid': 'reply'})
        if reply_elem:
            reply_span = reply_elem.find('span', {'data-testid': 'app-text-transition-container'})
            if reply_span:
                stats["Reply"] = reply_span.get_text(strip=True) or "0"
        
        retweet_elem = tweet_element.find('div', {'data-testid': 'retweet'})
        if retweet_elem:
            retweet_span = retweet_elem.find('span', {'data-testid': 'app-text-transition-container'})
            if retweet_span:
                stats["Retweet"] = retweet_span.get_text(strip=True) or "0"
        
        like_elem = tweet_element.find('div', {'data-testid': 'like'})
        if like_elem:
            like_span = like_elem.find('span', {'data-testid': 'app-text-transition-container'})
            if like_span:
                stats["Like"] = like_span.get_text(strip=True) or "0"
        
        views_elem = tweet_element.find('a', {'aria-label': lambda x: x and 'views' in x.lower()})
        if views_elem:
            views_text = views_elem.get('aria-label', '')
            views_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*views?', views_text, re.IGNORECASE)
            if views_match:
                stats["Views"] = views_match.group(1)
        
        if stats["Reply"] == "0":
            reply_alt = tweet_element.select_one('[aria-label*="repl"], [aria-label*="Repl"]')
            if reply_alt:
                aria_label = reply_alt.get('aria-label', '')
                reply_match = re.search(r'(\d+(?:,\d+)*)\s*repl', aria_label, re.IGNORECASE)
                if reply_match:
                    stats["Reply"] = reply_match.group(1)
        
        if stats["Retweet"] == "0":
            retweet_alt = tweet_element.select_one('[aria-label*="retweet"], [aria-label*="Retweet"]')
            if retweet_alt:
                aria_label = retweet_alt.get('aria-label', '')
                retweet_match = re.search(r'(\d+(?:,\d+)*)\s*retweet', aria_label, re.IGNORECASE)
                if retweet_match:
                    stats["Retweet"] = retweet_match.group(1)
        
        if stats["Like"] == "0":
            like_alt = tweet_element.select_one('[aria-label*="like"], [aria-label*="Like"]')
            if like_alt:
                aria_label = like_alt.get('aria-label', '')
                like_match = re.search(r'(\d+(?:,\d+)*)\s*like', aria_label, re.IGNORECASE)
                if like_match:
                    stats["Like"] = like_match.group(1)

        if stats["Views"] == "0":
            analytics_links = tweet_element.find_all('a', href=True)
            for link in analytics_links:
                aria_label = link.get('aria-label', '').lower()
                if 'view' in aria_label and ('tweet' in aria_label or 'analytic' in aria_label):
                    views_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)', aria_label)
                    if views_match:
                        stats["Views"] = views_match.group(1)
                        break
            
            if stats["Views"] == "0":
                view_elements = tweet_element.find_all('span')
                for elem in view_elements:
                    text = elem.get_text(strip=True)
                    if re.match(r'^\d+(?:,\d+)*(?:\.\d+)?[KMB]?$', text):
                        parent = elem.find_parent()
                        if parent and ('analytic' in str(parent).lower() or 'view' in str(parent).lower()):
                            stats["Views"] = text
    
    except Exception as e:
        print(f"Error extracting stats: {e}")
    
    for key in stats:
        stats[key] = stats[key].replace(",", "") if stats[key] else "0"
        if not stats[key] or stats[key] == "":
            stats[key] = "0"
    
    return stats

def extract_data(tweet, keyword):
    try:
        username_elem = tweet.find('div', {'data-testid': 'User-Name'})
        username = username_elem.get_text(strip=True) if username_elem else "Unknown"
        
        tweet_text_elem = tweet.find('div', {'data-testid': 'tweetText'})
        tweet_text = tweet_text_elem.get_text(strip=True) if tweet_text_elem else ""
        
        img_elem = tweet.find('img', {'alt': 'Image'})
        image_url = img_elem.get('src', '') if img_elem else ""
        
        time_elem = tweet.find('time')
        tweet_url = ""
        if time_elem and time_elem.find_parent('a'):
            href = time_elem.find_parent('a').get('href', '')
            if href:
                tweet_url = f"https://twitter.com{href}"
        
        timestamp = time_elem.get('datetime', '') if time_elem else ""
        
        stats = extract_engagement_stats(tweet)
        
        data = {
            "Username": username,
            "Tweet": tweet_text,
            "Image": image_url,
            "URL": tweet_url,
            "Tanggal_Tweet": timestamp,
            "Reply": stats["Reply"],
            "Retweet": stats["Retweet"],
            "Like": stats["Like"],
            "Views": stats["Views"],
            "Keyword": keyword,
            "Tanggal_Scrape": datetime.now().strftime("%Y-%m-%d")
        }
        
        return data
        
    except Exception as e:
        print(f"Error extracting tweet data: {e}")
        return None

def scrape_keyword(keyword):
    query = f"{keyword} since:{SINCE} until:{UNTIL}"
    if LANGUAGE:
        query += f" lang:{LANGUAGE}"
    
    url = f"https://twitter.com/search?q={query.replace(' ', '%20')}&src=typed_query&f=live"
    
    print(f"🔍 Searching: {url}")
    driver.get(url)
    time.sleep(SCROLL_DELAY + 2)
    
    seen = set()
    tweet_data = []
    no_new_count = 0
    
    for scroll_num in range(MAX_SCROLLS):
        print(f"📜 Scroll {scroll_num + 1}/{MAX_SCROLLS} untuk keyword: {keyword}")
        
        tweets = parse_tweets()
        print(f"Found {len(tweets)} tweet elements on page")
        
        new_data = 0
        for tweet in tweets:
            data = extract_data(tweet, keyword)
            if data and data["URL"] and data["URL"] not in seen:
                tweet_data.append(data)
                seen.add(data["URL"])
                new_data += 1
                print(f"✅ Tweet baru: {data['Username']} - Likes: {data['Like']}, RTs: {data['Retweet']}, Replies: {data['Reply']}, Views: {data['Views']}")
        
        if new_data == 0:
            no_new_count += 1
            print(f"⚠️ Tidak ada tweet baru di scroll ini ({no_new_count}/{NO_NEW_TWEETS_LIMIT})")
        else:
            no_new_count = 0
        
        if no_new_count >= NO_NEW_TWEETS_LIMIT:
            print(f"⏹️ Berhenti scrolling untuk: {keyword}")
            break
        
        scroll_down()
    
    print(f"📊 Total tweets untuk '{keyword}': {len(tweet_data)}")
    return tweet_data

if __name__ == "__main__":
    try:
        login()
        all_data = []
        
        for kw in KEYWORDS:
            print(f"\n🚀 Memulai scraping untuk: {kw}")
            tweets = scrape_keyword(kw)
            all_data.extend(tweets)
            time.sleep(SCROLL_DELAY + 2)
        
        if all_data:
            df = pd.DataFrame(all_data)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if OUTPUT_FORMAT.lower() == "json":
                filename = f"{OUTPUT_FILENAME}_{timestamp}.json"
                df.to_json(filename, orient='records', indent=2)
            elif OUTPUT_FORMAT.lower() == "excel":
                filename = f"{OUTPUT_FILENAME}_{timestamp}.xlsx"
                df.to_excel(filename, index=False)
            else: 
                filename = f"./output/{OUTPUT_FILENAME}_{timestamp}.csv"
                df.to_csv(filename, index=False, encoding='utf-8')
                
            print(f"✅ Selesai! Data disimpan ke {filename}")
            print(f"📊 Total tweets: {len(all_data)}")
            if len(df) > 0:
                print("\n📈 Sample engagement stats:")
                print(df[['Username', 'Like', 'Retweet', 'Reply', 'Views']].head())
        else:
            print("❌ Tidak ada data yang berhasil di-scrape")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        driver.quit()
        print("🔒 Browser ditutup")