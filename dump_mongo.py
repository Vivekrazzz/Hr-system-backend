import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('DB_HOST'))
db = client[os.getenv('DB_NAME', 'hr_system_db')]
coll = db['attendance_attendance']

for doc in coll.find():
    print(f"ID:{repr(doc.get('_id'))} EID:{repr(doc.get('employee_id'))} Date:{repr(doc.get('date'))}")
