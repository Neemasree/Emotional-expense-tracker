from django.db import models
from django.contrib.auth.models import User
from db_connector import MongoDBConnector

# Initialize MongoDB connector
mongo_db = MongoDBConnector()

class TriggerHabit(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_all_from_mongodb(cls):
        """Get all trigger habits from MongoDB"""
        return list(mongo_db.find('trigger_habits'))
    
    @classmethod
    def create_in_mongodb(cls, name, description=""):
        """Create a new trigger habit in MongoDB"""
        document = {
            'name': name,
            'description': description
        }
        return mongo_db.insert_one('trigger_habits', document)

class Expense(models.Model):
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('stressed', 'Stressed'),
        ('bored', 'Bored'),
        ('anxious', 'Anxious'),
        ('neutral', 'Neutral'),
    ]
    
    REGRET_CHOICES = [
        ('essential', 'Essential'),
        ('treat', 'Treat'),
        ('impulse', 'Impulse'),
        ('regretted', 'Regretted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100)
    
    # Emotional features
    emotion = models.CharField(max_length=50, choices=EMOTION_CHOICES, blank=True)
    regret_level = models.CharField(max_length=50, choices=REGRET_CHOICES, blank=True)
    trigger_habits = models.ManyToManyField(TriggerHabit, blank=True)
    
    def __str__(self):
        return f"{self.amount} - {self.description[:30]}"
    
    @classmethod
    def create_in_mongodb(cls, user_id, amount, description, category, emotion, regret_level, trigger_habits):
        """Create a new expense in MongoDB"""
        from django.utils import timezone
        
        document = {
            'user_id': user_id,
            'amount': float(amount),
            'description': description,
            'date': timezone.now(),
            'category': category,
            'emotion': emotion,
            'regret_level': regret_level,
            'trigger_habits': trigger_habits
        }
        
        return mongo_db.insert_one('expenses', document)
    
    @classmethod
    def get_user_expenses(cls, user_id, limit=None):
        """Get expenses for a specific user from MongoDB"""
        query = {'user_id': user_id}
        cursor = mongo_db.find('expenses', query)
        
        # Sort by date descending
        cursor = cursor.sort('date', -1)
        
        # Apply limit if specified
        if limit:
            cursor = cursor.limit(limit)
            
        return list(cursor)
    
    @classmethod
    def get_expense_analytics(cls, user_id):
        """Get analytics data for expenses from MongoDB"""
        # Get data for charts - emotions
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$group': {'_id': '$emotion', 'count': {'$sum': 1}, 'total': {'$sum': '$amount'}}},
        ]
        emotions_data = list(mongo_db.aggregate('expenses', pipeline))
        
        # Get data for charts - trigger habits
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$unwind': '$trigger_habits'},
            {'$group': {'_id': '$trigger_habits', 'count': {'$sum': 1}, 'total': {'$sum': '$amount'}}},
        ]
        triggers_data = list(mongo_db.aggregate('expenses', pipeline))
        
        # Get data for charts - regret levels
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$group': {'_id': '$regret_level', 'count': {'$sum': 1}, 'total': {'$sum': '$amount'}}},
        ]
        regret_data = list(mongo_db.aggregate('expenses', pipeline))
        
        return {
            'emotions_data': emotions_data,
            'triggers_data': triggers_data,
            'regret_data': regret_data
        }

class Challenge(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    points_reward = models.IntegerField(default=10)
    
    def __str__(self):
        return self.title
    
    @classmethod
    def create_in_mongodb(cls, user_id, title, description, end_date, points_reward=10):
        """Create a new challenge in MongoDB"""
        from django.utils import timezone
        
        document = {
            'user_id': user_id,
            'title': title,
            'description': description,
            'start_date': timezone.now(),
            'end_date': end_date,
            'status': 'active',
            'points_reward': points_reward
        }
        
        return mongo_db.insert_one('challenges', document)
    
    @classmethod
    def get_active_challenges(cls, user_id):
        """Get active challenges for a user from MongoDB"""
        query = {'user_id': user_id, 'status': 'active'}
        return list(mongo_db.find('challenges', query))
    
    @classmethod
    def complete_challenge(cls, challenge_id, user_id):
        """Mark a challenge as completed in MongoDB"""
        query = {'_id': challenge_id, 'user_id': user_id}
        update = {'$set': {'status': 'completed'}}
        return mongo_db.update_one('challenges', query, update)




