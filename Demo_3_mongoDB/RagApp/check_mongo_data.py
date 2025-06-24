from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["newsdb"]
collection = db["news_data"]  # make sure this is the right collection

for doc in collection.find().limit(5):
    print("----------")
    for key in doc.keys():
        print(f"{key} => {doc[key]}")
