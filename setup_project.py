import os
import sys
import subprocess
import shutil

def create_directory_structure():
    """Create the necessary directory structure for the project"""
    print("Creating directory structure...")
    
    # Create app directories if they don't exist
    for directory in ['expenses', 'users', 'templates', 'static']:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created {directory} directory")
    
    # Create subdirectories
    for app in ['expenses', 'users']:
        for subdir in ['templates', 'static']:
            path = os.path.join(app, subdir, app)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                print(f"Created {path} directory")
    
    # Create media directory
    if not os.path.exists('media'):
        os.makedirs('media')
        print("Created media directory")
    
    print("Directory structure created successfully!")

def install_django():
    """Install Django and other requirements"""
    print("Installing Django and requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "django==5.1.1", "pymongo==4.6.1"], check=True)
        print("Django and PyMongo installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing Django: {e}")
        return False

def setup_django_project():
    """Set up the Django project"""
    print("Setting up Django project...")
    
    # Check if manage.py exists
    if not os.path.exists('manage.py'):
        print("Creating Django project files...")
        try:
            # Create a temporary project to get the necessary files
            subprocess.run([sys.executable, "-m", "django", "startproject", "temp_project"], check=True)
            
            # Copy the manage.py file
            shutil.copy('temp_project/manage.py', 'manage.py')
            
            # Update the settings module in manage.py
            with open('manage.py', 'r') as file:
                content = file.read()
            
            content = content.replace('temp_project.settings', 'emotional_expense_tracker.settings')
            
            with open('manage.py', 'w') as file:
                file.write(content)
            
            # Create the emotional_expense_tracker directory if it doesn't exist
            if not os.path.exists('emotional_expense_tracker'):
                os.makedirs('emotional_expense_tracker')
            
            # Copy necessary files from temp_project
            for file_name in ['__init__.py', 'asgi.py', 'wsgi.py']:
                source = os.path.join('temp_project', 'temp_project', file_name)
                destination = os.path.join('emotional_expense_tracker', file_name)
                shutil.copy(source, destination)
            
            # Clean up temporary project
            shutil.rmtree('temp_project')
            
            print("Django project files created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error setting up Django project: {e}")
            return False
    else:
        print("Django project already exists.")
    
    return True

def setup():
    """Main setup function"""
    print("=" * 50)
    print("Emotional Expense Tracker - Project Setup")
    print("=" * 50)
    
    # Install Django
    print("\nStep 1: Installing Django...")
    if not install_django():
        print("\nFailed to install Django. Please check your Python installation.")
        return False
    
    # Create directory structure
    print("\nStep 2: Creating directory structure...")
    create_directory_structure()
    
    # Set up Django project
    print("\nStep 3: Setting up Django project...")
    if not setup_django_project():
        print("\nFailed to set up Django project.")
        return False
    
    print("\n" + "=" * 50)
    print("Project setup completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Run 'python setup_windows.py' to set up MongoDB")
    print("2. Run 'python manage.py migrate' to create the database")
    print("3. Run 'python manage.py runserver' to start the development server")
    
    return True

if __name__ == "__main__":
    setup()