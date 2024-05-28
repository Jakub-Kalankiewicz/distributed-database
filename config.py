import os


class Config:
    MONGO_URI_1 = os.getenv('MONGO_URI_1', 'mongodb://localhost:27017/mongodb1')
    MONGO_URI_2 = os.getenv('MONGO_URI_2', 'mongodb://localhost:27017/mongodb2')
    MAX_WORKERS = 4
