from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from db_connector import MongoDBConnector
from collections import Counter

# Initialize MongoDB connector
mongo_db = MongoDBConnector()

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            
            # Create user profile in MongoDB
            mongo_db.insert_one('user_profiles', {
                'user_id': user.id,
                'points': 0,
                'badges': {}
            })
            
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    # Get user profile from MongoDB
    user_profile = mongo_db.find_one('user_profiles', {'user_id': request.user.id})
    
    if not user_profile:
        # Create profile if it doesn't exist
        user_profile = {
            'user_id': request.user.id,
            'points': 0,
            'badges': {}
        }
        mongo_db.insert_one('user_profiles', user_profile)
    
    # Get user's expenses
    expenses = list(mongo_db.find('expenses', {'user_id': request.user.id}))
    
    # Calculate total expenses
    total_expenses = sum(expense.get('amount', 0) for expense in expenses)
    
    # Find most common emotion
    emotions = [expense.get('emotion') for expense in expenses if expense.get('emotion')]
    most_common_emotion = Counter(emotions).most_common(1)[0][0] if emotions else 'None'
    
    # Find most expensive category
    categories = {}
    for expense in expenses:
        category = expense.get('category')
        if category:
            if category not in categories:
                categories[category] = 0
            categories[category] += expense.get('amount', 0)
    
    most_expensive_category = max(categories.items(), key=lambda x: x[1])[0] if categories else 'None'
    
    # Find most common trigger habit
    all_triggers = []
    for expense in expenses:
        triggers = expense.get('trigger_habits', [])
        all_triggers.extend(triggers)
    
    most_common_trigger = Counter(all_triggers).most_common(1)[0][0] if all_triggers else 'None'
    
    # Get completed challenges
    completed_challenges = list(mongo_db.find('challenges', {
        'user_id': request.user.id,
        'status': 'completed'
    }))
    
    context = {
        'user_profile': user_profile,
        'total_expenses': total_expenses,
        'most_common_emotion': most_common_emotion,
        'most_expensive_category': most_expensive_category,
        'most_common_trigger': most_common_trigger,
        'completed_challenges': completed_challenges
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def award_badge(request, badge_name):
    """Award a badge to the user"""
    # Get user profile
    user_profile = mongo_db.find_one('user_profiles', {'user_id': request.user.id})
    
    if not user_profile:
        messages.error(request, 'User profile not found!')
        return redirect('profile')
    
    # Define badge info
    badge_info = {
        'saver': {'icon': 'piggy-bank', 'description': 'Completed 3 saving challenges'},
        'mindful': {'icon': 'brain', 'description': 'Tracked emotions for 10 expenses'},
        'aware': {'icon': 'eye', 'description': 'Identified 5 different trigger habits'}
    }
    
    if badge_name in badge_info:
        # Update user profile with new badge
        badges = user_profile.get('badges', {})
        badges[badge_name] = badge_info[badge_name]
        
        mongo_db.update_one('user_profiles', 
                           {'user_id': request.user.id}, 
                           {'$set': {'badges': badges}})
        
        messages.success(request, f'You earned the {badge_name.title()} badge!')
    else:
        messages.error(request, 'Invalid badge!')
    
    return redirect('profile')

def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')  # Redirect to login page instead of home




