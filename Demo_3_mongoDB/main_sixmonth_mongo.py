#############################################
# store the six omnth data into the mongo db database by using this url. 
################################################

import pymongo
import json

if __name__ == '__main__':
    print("Connecting to MongoDB...")

    # Connect to local MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['newsdb']  # Use or create database
    collection = db['news_data']  # Use or create collection

    # Load data from JSON file
    try:
        with open("News_Platform_old_data/All_Hip_Hop.json", "r", encoding="utf-8") as file:
            data = json.load(file)

            # Ensure the file contains a list of documents
            if isinstance(data, list):
                # Insert all documents into MongoDB
                collection.insert_many(data)
                print(f" Successfully inserted {len(data)} documents into MongoDB.")
            else:
                print(" JSON file should contain a list of documents.")
    except Exception as e:
        print(f" Error reading or inserting data: {e}")
