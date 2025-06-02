from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bson import ObjectId
from .forms import ExpenseForm, ChallengeForm
from .services import EmotionPredictor, RegretPredictor, TrendAnalyzer
from db_connector import MongoDBConnector

# Initialize MongoDB connector
mongo_db = MongoDBConnector()
emotion_predictor = EmotionPredictor()
regret_predictor = RegretPredictor()
trend_analyzer = TrendAnalyzer()

@login_required
def dashboard(request):
    # Get recent expenses
    recent_expenses = list(mongo_db.find('expenses', 
                                        {'user_id': request.user.id}, 
                                        ).sort('date', -1).limit(5))
    
    # Get active challenges
    active_challenges = list(mongo_db.find('challenges', 
                                          {'user_id': request.user.id, 'status': 'active'}))
    
    # Get spending trends
    trend_alerts = trend_analyzer.detect_spending_trends(request.user.id)
    
    context = {
        'recent_expenses': recent_expenses,
        'active_challenges': active_challenges,
        'trend_alerts': trend_alerts
    }
    
    return render(request, 'expenses/dashboard.html', context)

@login_required
def expense_list(request):
    expenses = list(mongo_db.find('expenses', {'user_id': request.user.id}).sort('date', -1))
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            # Get form data
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            category = form.cleaned_data['category']
            regret_level = form.cleaned_data['regret_level']
            trigger_habits = form.cleaned_data.get('trigger_habits', [])
            
            # Predict emotion from description
            emotion = emotion_predictor.predict_emotion(description)
            
            # Create expense in MongoDB
            expense_id = mongo_db.insert_one('expenses', {
                'user_id': request.user.id,
                'amount': float(amount),
                'description': description,
                'category': category,
                'emotion': emotion,
                'regret_level': regret_level,
                'trigger_habits': trigger_habits,
                'date': request.POST.get('date') or None
            })
            
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    
    return render(request, 'expenses/add_expense.html', {'form': form})

def safe_label(item):
    return item.get('_id') if item.get('_id') else "Unknown"

@login_required
def expense_analytics(request):
    def process_data(data):
        for item in data:
            item['label'] = item.get('_id', 'Unknown')  # create 'label' key
        return data

    # Process analytics
    emotions_data = process_data(list(mongo_db.aggregate('expenses', [
        {'$match': {'user_id': request.user.id}},
        {'$group': {'_id': '$emotion', 'count': {'$sum': 1}, 'total': {'$sum': '$amount'}}},
    ])))

    triggers_data = process_data(list(mongo_db.aggregate('expenses', [
        {'$match': {'user_id': request.user.id}},
        {'$unwind': '$trigger_habits'},
        {'$group': {'_id': '$trigger_habits', 'count': {'$sum': 1}, 'total': {'$sum': '$amount'}}},
    ])))

    regret_data = process_data(list(mongo_db.aggregate('expenses', [
        {'$match': {'user_id': request.user.id}},
        {'$group': {'_id': '$regret_level', 'count': {'$sum': 1}, 'total': {'$sum': '$amount'}}},
    ])))

    category_data = process_data(list(mongo_db.aggregate('expenses', [
        {'$match': {'user_id': request.user.id}},
        {'$group': {'_id': '$category', 'total': {'$sum': '$amount'}}},
    ])))

    context = {
        'emotions_data': emotions_data,
        'triggers_data': triggers_data,
        'regret_data': regret_data,
        'category_data': category_data
    }

    return render(request, 'expenses/analytics.html', context)


@login_required
def create_challenge(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            # Get form data
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            end_date = form.cleaned_data['end_date']
            points_reward = form.cleaned_data['points_reward']
            
            # Create challenge in MongoDB
            challenge_id = mongo_db.insert_one('challenges', {
                'user_id': request.user.id,
                'title': title,
                'description': description,
                'start_date': None,  # Will be set by MongoDB
                'end_date': end_date,
                'status': 'active',
                'points_reward': points_reward
            })
            
            messages.success(request, 'Challenge created successfully!')
            return redirect('dashboard')
    else:
        form = ChallengeForm()
    
    return render(request, 'expenses/create_challenge.html', {'form': form})

@login_required
def complete_challenge(request, challenge_id):
    # Find the challenge
    challenge = mongo_db.find_one('challenges', {'_id': ObjectId(challenge_id), 'user_id': request.user.id})
    
    if not challenge:
        messages.error(request, 'Challenge not found!')
        return redirect('dashboard')
    
    # Update challenge status
    mongo_db.update_one('challenges', 
                       {'_id': ObjectId(challenge_id)}, 
                       {'$set': {'status': 'completed'}})
    
    # Award points to user
    points_reward = challenge.get('points_reward', 10)
    user_profile = mongo_db.find_one('user_profiles', {'user_id': request.user.id})
    
    if user_profile:
        current_points = user_profile.get('points', 0)
        mongo_db.update_one('user_profiles', 
                           {'user_id': request.user.id}, 
                           {'$set': {'points': current_points + points_reward}})
    else:
        # Create user profile if it doesn't exist
        mongo_db.insert_one('user_profiles', {
            'user_id': request.user.id,
            'points': points_reward,
            'badges': {}
        })
    
    messages.success(request, f'Challenge completed! You earned {points_reward} points!')
    return redirect('dashboard')

@login_required
def predict_regret(request):
    """API endpoint to predict regret likelihood"""
    if request.method == 'POST':
        category = request.POST.get('category')
        amount = float(request.POST.get('amount', 0))
        trigger_habits = request.POST.getlist('trigger_habits')
        
        # Use the RegretPredictor to predict regret likelihood
        regret_likelihood = regret_predictor.predict_regret_likelihood(
            request.user.id, category, amount, trigger_habits
        )
        
        return JsonResponse({
            'regret_likelihood': regret_likelihood,
            'message': get_regret_message(regret_likelihood)
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_regret_message(likelihood):
    """Get a message based on regret likelihood"""
    if likelihood < 0.3:
        return "This purchase seems reasonable."
    elif likelihood < 0.6:
        return "You might regret this purchase later."
    else:
        return "High chance you'll regret this purchase!"

@login_required
def trigger_habits(request):
    """View to manage trigger habits"""
    if request.method == 'POST':
        # Handle adding a new trigger habit
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            # Create new trigger habit
            mongo_db.insert_one('trigger_habits', {
                'name': name,
                'description': description
            })
            messages.success(request, 'Trigger habit added successfully!')
            return redirect('trigger_habits')
    
    # Get all trigger habits
    all_habits = list(mongo_db.find('trigger_habits'))
    
    # Get user's expenses with trigger habits
    pipeline = [
        {'$match': {'user_id': request.user.id}},
        {'$unwind': '$trigger_habits'},
        {'$group': {'_id': '$trigger_habits', 'count': {'$sum': 1}, 'total': {'$sum': '$amount'}}},
        {'$sort': {'count': -1}}
    ]
    user_habits_data = list(mongo_db.aggregate('expenses', pipeline))
    
    context = {
        'all_habits': all_habits,
        'user_habits_data': user_habits_data
    }
    
    return render(request, 'expenses/trigger_habits.html', context)































