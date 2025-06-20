import json
import os
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load .env
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Load JSON
with open("hiphop_dx_sixmonth_articles_updated.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

#Convert date string like 'Jun 16, 2025, 2:00 PM' → '2025-06-16'
def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%B %d, %Y %I:%M %p").date().isoformat()
    except Exception as e:
        print(f"[⚠️] Failed to parse date: {date_str} → {e}")
        return "1970-01-01"
    
# Insert one article
def insert_article(tx, article):
    tx.run(
        """
        MERGE (a:Article {title: $title})
        SET a.description = $description,
            a.publication_date = date($publication_date),
            a.full_text = $full_text

        MERGE (au:Author {name: $author})
        MERGE (s:Source {name: $source})
        MERGE (u:URL {url: $source_url})
        MERGE (sec:Section {name: $section})

        MERGE (au)-[:WROTE]->(a)
        MERGE (a)-[:PUBLISHED_BY]->(s)
        MERGE (a)-[:HAS_URL]->(u)
        MERGE (a)-[:BELONGS_TO]->(sec)
        """,
        title=article.get("title", "Untitled"),
        description=article.get("description", ""),
        publication_date=parse_date(article.get("publication_date", "")),
        author=article.get("author", "Unknown"),
        source=article.get("source", "Unknown"),
        source_url=article.get("source_url", ""),
        section=article.get("section", "General"),
        full_text=article.get("description", ""),
    )

# Insert all
def insert_all_articles():
    with driver.session() as session:
        for idx, article in enumerate(articles, start=1):
            try:
                session.execute_write(insert_article, article)
                print(f"✅ Inserted {idx}/{len(articles)}: {article.get('title')}")
            except Exception as e:
                print(f"❌ Failed to insert article {idx}: {e}")

# Main
if __name__ == "__main__":
    insert_all_articles()
