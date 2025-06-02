import os
import sys
import subprocess
import time

def check_mongodb_connection():
    """Check if MongoDB is running"""
    try:
        from pymongo import MongoClient
        client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)
        client.server_info()  # Will raise an exception if MongoDB is not running
        print("MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"ERROR: Could not connect to MongoDB: {e}")
        return False

def install_requirements():
    """Install Python requirements"""
    print("Installing Python requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def initialize_mongodb():
    """Initialize MongoDB with default data"""
    print("Initializing MongoDB...")
    try:
        subprocess.run([sys.executable, "init_mongodb.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error initializing MongoDB: {e}")
        return False

def setup():
    """Main setup function"""
    print("=" * 50)
    print("Emotional Expense Tracker - MongoDB Setup")
    print("=" * 50)
    
    # Check MongoDB connection
    print("\nStep 1: Checking MongoDB connection...")
    if not check_mongodb_connection():
        print("\nMongoDB connection failed. Please make sure MongoDB is installed and running.")
        print("\nInstallation instructions:")
        print("1. Download MongoDB Community Server from https://www.mongodb.com/try/download/community")
        print("2. Install MongoDB and make sure the service is running")
        print("3. Run this setup script again")
        return False
    
    # Install requirements
    print("\nStep 2: Installing Python requirements...")
    if not install_requirements():
        print("\nFailed to install requirements. Please check your Python installation.")
        return False
    
    # Initialize MongoDB
    print("\nStep 3: Initializing MongoDB...")
    if not initialize_mongodb():
        print("\nFailed to initialize MongoDB. Please check the error message above.")
        return False
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("=" * 50)
    print("\nYou can now run the Django server with:")
    print("python manage.py runserver")
    
    return True

if __name__ == "__main__":
    setup()