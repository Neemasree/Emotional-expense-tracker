from db_connector import MongoDBConnector
import sys

def initialize_mongodb():
    """Initialize MongoDB with default collections and data"""
    try:
        # Connect to MongoDB
        mongo_db = MongoDBConnector()
        print("Connected to MongoDB successfully!")
        
        # Create collections if they don't exist
        collections = mongo_db.db.list_collection_names()
        
        # Initialize trigger habits collection with default data
        if 'trigger_habits' not in collections:
            print("Creating trigger_habits collection...")
            default_habits = [
                {'name': 'Late-night craving', 'description': 'Spending due to hunger or cravings late at night'},
                {'name': 'Social pressure', 'description': 'Spending to fit in with friends or colleagues'},
                {'name': 'Payday impulse', 'description': 'Impulse spending right after getting paid'},
                {'name': 'Boredom', 'description': 'Spending to alleviate boredom'},
                {'name': 'Stress relief', 'description': 'Spending to cope with stress or anxiety'}
            ]
            
            for habit in default_habits:
                mongo_db.insert_one('trigger_habits', habit)
        
        # Ensure other collections exist
        for collection in ['expenses', 'challenges', 'user_profiles']:
            if collection not in collections:
                print(f"Creating {collection} collection...")
                mongo_db.db.create_collection(collection)
        
        print("MongoDB initialization complete!")
        return True
        
    except Exception as e:
        print(f"Error initializing MongoDB: {e}")
        return False

if __name__ == "__main__":
    print("Initializing MongoDB for Emotional Expense Tracker...")
    success = initialize_mongodb()
    if success:
        print("\nSetup complete! You can now run the Django server with:")
        print("python manage.py runserver")
        sys.exit(0)
    else:
        print("\nFailed to initialize MongoDB. Please check your MongoDB installation and try again.")
        sys.exit(1)

