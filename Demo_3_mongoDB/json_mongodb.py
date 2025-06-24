#############################################
# daily web scraper and store this data into the mongodb 
################################################



import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from datetime import datetime
from dateutil import parser
import pymongo

# Configuration
DELAY = 1
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "newsdb"
COLLECTION_NAME = "news_data"

def connect_to_mongo():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    return collection

def get_existing_urls(collection):
    return {doc["source_url"] for doc in collection.find({}, {"source_url": 1})}

def scrape_hiphopdx():
    BASE_URL = "https://hiphopdx.com/news/{}"
    collection = connect_to_mongo()
    existing_urls = get_existing_urls(collection)

    today_date = datetime.now().date()
    print(f"🔍 Looking for articles published on: {today_date.strftime('%B %d, %Y')}")

    new_articles = []

    for page_num in range(0, 1):  # Usually only page 0 contains today's articles
        page_url = BASE_URL.format(page_num)
        print(f"\n🔗 Scraping page: {page_url}")

        try:
            response = requests.get(page_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            article_links = soup.select('div.secondary-posts a')
            stop_scraping = False

            for a_tag in article_links:
                href = a_tag.get('href')
                if not href:
                    continue

                full_url = urljoin(page_url, href)

                # Skip if already in MongoDB
                if full_url in existing_urls:
                    print(f"⏭ Skipping already stored: {full_url}")
                    continue

                try:
                    article_response = requests.get(full_url)
                    article_soup = BeautifulSoup(article_response.content, 'html.parser')

                    date_elem = article_soup.select_one('.date')
                    if not date_elem:
                        continue

                    raw_date_text = date_elem.get_text(strip=True).replace("Published on:", "").strip()
                    parsed_date = parser.parse(raw_date_text)
                    article_date = parsed_date.date()

                    if article_date != today_date:
                        print(f"⏭ Skipping (Not today): {raw_date_text}")
                        stop_scraping = True
                        continue

                    title = article_soup.select_one('.headline__title').get_text(strip=True) if article_soup.select_one('.headline__title') else "No title"

                    description = ""
                    body = article_soup.select_one('.body-copy')
                    if body:
                        paragraphs = body.find_all('p')
                        description = "\n".join(p.get_text(strip=True) for p in paragraphs)

                    author = article_soup.select_one('.author a').get_text(strip=True) if article_soup.select_one('.author a') else "Unknown"

                    article_data = {
                        "source_url": full_url,
                        "title": title,
                        "description": description,
                        "author": author,
                        "publication_date": parsed_date.strftime("%B %d, %Y %I:%M %p")
                    }

                    # Store in MongoDB
                    collection.insert_one(article_data)
                    print(f"✅ Inserted: {title}")
                    time.sleep(DELAY)

                except Exception as e:
                    print(f"❌ Failed article: {full_url}\nError: {e}")

            if stop_scraping:
                print("⛔ Reached non-today article, stopping early.")
                break

        except Exception as e:
            print(f"❌ Failed to scrape page: {page_url}\nError: {e}")
        time.sleep(DELAY)

def main():
    scrape_hiphopdx()
    print("\n✅ Done scraping today's articles and saving to MongoDB.")

if __name__ == "__main__":
    main()