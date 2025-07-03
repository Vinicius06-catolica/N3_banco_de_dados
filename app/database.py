from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

connection = os.getenv("CONNECTION_STRING")
client = MongoClient(connection)
db = client['martim_python']
collection = db['albuns']
