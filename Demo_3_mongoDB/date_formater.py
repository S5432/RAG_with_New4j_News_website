import json
from datetime import datetime
import re

# D:\Final Scraped data in Mongodb\News_Platform_old_data\Hip_Hop_Dx.json
# Load the JSON file
with open("News_Platform_old_data/Hip_Hop_Dx.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def clean_and_format_date(date_str):
    # Step 1: Remove trailing timezone info (e.g., 'PST', 'EST')
    date_str = re.sub(r"\s+(PST|EST|CST|IST|UTC|GMT|[A-Z]{3,4})$", "", date_str.strip())

    # Step 2: Try parsing with short or full month names
    for fmt in ("%b %d, %Y, %I:%M %p", "%B %d, %Y, %I:%M %p", "%b %d, %Y %I:%M %p", "%B %d, %Y %I:%M %p"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%B %d, %Y %I:%M %p")
        except ValueError:
            continue

    print(f"⚠️ Failed to convert: {date_str}")
    return date_str  # return as-is if no format works

# Update all articles
for article in data:
    if "publication_date" in article:
        article["publication_date"] = clean_and_format_date(article["publication_date"])

# Save updated file
with open("Data/hiphop_dx_sixmonth_articles_updated.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ JSON file updated with clean full-format publication dates.")
