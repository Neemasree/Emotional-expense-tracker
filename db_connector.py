import pymongo
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoDBConnector:
    def __init__(self):
        """Initialize MongoDB connection"""
        # Get MongoDB connection string from environment variables or use default
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGO_DB_NAME', 'emotional_expense_tracker')
        
        # Connect to MongoDB
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[db_name]
    
    def find(self, collection_name, query=None, projection=None):
        """Find documents in a collection"""
        if query is None:
            query = {}
        return self.db[collection_name].find(query, projection)
    
    def find_one(self, collection_name, query=None, projection=None):
        """Find a single document in a collection"""
        if query is None:
            query = {}
        return self.db[collection_name].find_one(query, projection)
    
    def insert_one(self, collection_name, document):
        """Insert a document into a collection"""
        result = self.db[collection_name].insert_one(document)
        return str(result.inserted_id)
    
    def insert_many(self, collection_name, documents):
        """Insert multiple documents into a collection"""
        result = self.db[collection_name].insert_many(documents)
        return [str(id) for id in result.inserted_ids]
    
    def update_one(self, collection_name, query, update):
        """Update a document in a collection"""
        return self.db[collection_name].update_one(query, update)
    
    def update_many(self, collection_name, query, update):
        """Update multiple documents in a collection"""
        return self.db[collection_name].update_many(query, update)
    
    def delete_one(self, collection_name, query):
        """Delete a document from a collection"""
        return self.db[collection_name].delete_one(query)
    
    def delete_many(self, collection_name, query):
        """Delete multiple documents from a collection"""
        return self.db[collection_name].delete_many(query)
    
    def aggregate(self, collection_name, pipeline):
        """Perform an aggregation on a collection"""
        return self.db[collection_name].aggregate(pipeline)



# Helper function to serialize MongoDB ObjectId to string for JSON
def json_serialize_mongodb(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


