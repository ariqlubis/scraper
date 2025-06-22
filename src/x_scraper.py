# src/x_scraper.py
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

# Setup browser
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

EXCLUDE_USER = "@bankbsi_id"

def login():
    try:
        driver.get("https://twitter.com/i/flow/login")
        # Input username
        username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
        username_input.send_keys(USERNAME)
        # Next
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]/..')))
        next_button.click()
        time.sleep(2)
        # Input password
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
        password_input.send_keys(PASSWORD)
        # Login
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
    stats = {"Reply": "0", "Retweet": "0", "Like": "0", "Views": "0"}
    try:
        # reply
        elem = tweet_element.find('div', {'data-testid': 'reply'})
        if elem and elem.find('span', {'data-testid': 'app-text-transition-container'}):
            stats['Reply'] = elem.find('span', {'data-testid': 'app-text-transition-container'}).get_text(strip=True) or '0'
        # retweet
        elem = tweet_element.find('div', {'data-testid': 'retweet'})
        if elem and elem.find('span', {'data-testid': 'app-text-transition-container'}):
            stats['Retweet'] = elem.find('span', {'data-testid': 'app-text-transition-container'}).get_text(strip=True) or '0'
        # like
        elem = tweet_element.find('div', {'data-testid': 'like'})
        if elem and elem.find('span', {'data-testid': 'app-text-transition-container'}):
            stats['Like'] = elem.find('span', {'data-testid': 'app-text-transition-container'}).get_text(strip=True) or '0'
        # views
        view_elem = tweet_element.find('a', {'aria-label': lambda x: x and 'views' in x.lower()})
        if view_elem:
            m = re.search(r"(\d+(?:[\d,]*)(?:\.\d+)?[KMB]?)", view_elem['aria-label'])
            if m: stats['Views'] = m.group(1)
    except Exception as e:
        print(f"Error extracting stats: {e}")
    # cleanup
    for k,v in stats.items():
        stats[k] = v.replace(',', '') if v else '0'
    return stats


def extract_data(tweet, keyword):
    try:
        user_elem = tweet.find('div', {'data-testid': 'User-Name'})
        username = user_elem.get_text(strip=True) if user_elem else 'Unknown'
        if EXCLUDE_USER.lower() in username.lower():
            return None
        # text
        text_elem = tweet.find('div', {'data-testid': 'tweetText'})
        text = text_elem.get_text(strip=True) if text_elem else ''
        # url
        time_elem = tweet.find('time')
        url = ''
        if time_elem and time_elem.parent.name == 'a':
            url = f"https://twitter.com{time_elem.parent['href']}"
        timestamp = time_elem['datetime'] if time_elem else ''
        stats = extract_engagement_stats(tweet)
        return {
            'Username': username,
            'Tweet': text,
            'URL': url,
            'Tanggal_Tweet': timestamp,
            'Reply': stats['Reply'],
            'Retweet': stats['Retweet'],
            'Like': stats['Like'],
            'Views': stats['Views'],
            'Keyword': keyword,
            'Tanggal_Scrape': datetime.now().strftime('%Y-%m-%d')
        }
    except Exception as e:
        print(f"Error extract data: {e}")
        return None



def scrape_keyword(keyword):
    query = f"{keyword} since:{SINCE} until:{UNTIL}" + (f" lang:{LANGUAGE}" if LANGUAGE else '')
    url = f"https://twitter.com/search?q={query.replace(' ', '%20')}&f=live"
    print(f"🔍 Searching: {url}")
    driver.get(url)
    time.sleep(SCROLL_DELAY+2)
    seen = set(); data=[]; no_new=0
    for i in range(MAX_SCROLLS):
        print(f"⏳ Scroll {i+1}/{MAX_SCROLLS} untuk '{keyword}'")
        tweets = parse_tweets()
        new=0
        for t in tweets:
            d = extract_data(t, keyword)
            if d and d['URL'] and d['URL'] not in seen:
                data.append(d); seen.add(d['URL']); new+=1
                print(f"➕ {d['Username']} ({d['Like']} likes, {d['Retweet']} rt)")
        if new==0:
            no_new+=1
            if no_new>=NO_NEW_TWEETS_LIMIT: break
        else:
            no_new=0
        scroll_down()
    print(f"✅ '{keyword}' total: {len(data)} tweets")
    return data

if __name__ == '__main__':
    try:
        login()
        all=[]
        for k in KEYWORDS:
            all+=scrape_keyword(k)
            time.sleep(SCROLL_DELAY+2)
        df = pd.DataFrame(all)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = 'json' if OUTPUT_FORMAT=='json' else 'xlsx' if OUTPUT_FORMAT=='excel' else 'csv'
        fname=f"output/{OUTPUT_FILENAME}_{ts}.{ext}"
        if OUTPUT_FORMAT=='json': df.to_json(fname, orient='records', indent=2)
        elif OUTPUT_FORMAT=='excel': df.to_excel(fname, index=False)
        else: df.to_csv(fname, index=False)
        print(f"✅ Done! saved: {fname}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
        print("🔒 Browser closed")
