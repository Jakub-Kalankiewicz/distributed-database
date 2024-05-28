from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient

from config import Config

app = Flask(__name__, template_folder='../templates')
app.config.from_object(Config)
CORS(app)

client1 = MongoClient(app.config['MONGO_URI_1'])
client2 = MongoClient(app.config['MONGO_URI_2'])
db1 = client1.get_database()
db2 = client2.get_database()

from app import routes
