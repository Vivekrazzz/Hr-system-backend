import os
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi

load_dotenv()
uri = os.getenv('DB_HOST')
client = MongoClient(uri, tlsAllowInvalidCertificates=True)
db = client[os.getenv('DB_NAME', 'hr_system_db')]

print("--- Collections ---")
for coll in db.list_collection_names():
    print(f"Collection: {coll}")
    for index in db[coll].list_indexes():
        print(f"  Index: {index}")
