from textblob import TextBlob
import re
from db_connector import MongoDBConnector

# Initialize MongoDB connector
mongo_db = MongoDBConnector()

class EmotionPredictor:
    def __init__(self):
        # Simple keyword-based emotion detection
        self.emotion_keywords = {
            'happy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'celebrate', 'treat', 'reward'],
            'sad': ['sad', 'depressed', 'unhappy', 'bad day', 'terrible', 'miserable', 'lonely'],
            'angry': ['angry', 'frustrated', 'annoyed', 'mad', 'furious', 'irritated'],
            'bored': ['bored', 'nothing to do', 'dull', 'monotonous', 'routine'],
            'stressed': ['stressed', 'anxious', 'pressure', 'overwhelmed', 'worried', 'tension']
        }
    
    def predict_emotion(self, text):
        # Convert to lowercase for better matching
        text = text.lower()
        
        # Check for emotion keywords
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return emotion
        
        # If no keywords match, use sentiment analysis as fallback
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        
        if sentiment > 0.2:
            return 'happy'
        elif sentiment < -0.2:
            return 'sad'
        else:
            return 'neutral'

class RegretPredictor:
    def predict_regret_likelihood(self, user_id, category, amount, trigger_habits):
        """
        Predicts likelihood of regret based on user's past expenses
        Returns a value between 0-1 representing regret likelihood
        """
        # Get user's past expenses with regret ratings from MongoDB
        past_expenses = list(mongo_db.find('expenses', {
            'user_id': user_id,
            'category': category,
            'regret_level': {'$in': ['impulse', 'regretted']}
        }))
        
        if not past_expenses:
            # No past data to base prediction on
            return 0.3  # Default moderate likelihood
        
        # Calculate regret likelihood based on similar past expenses
        regretted_count = sum(1 for expense in past_expenses if expense.get('regret_level') == 'regretted')
        total_count = len(past_expenses)
        
        if total_count == 0:
            return 0.3
            
        return regretted_count / total_count

class TrendAnalyzer:
    def detect_spending_trends(self, user_id, days=21):
        """
        Detects spending trends over the specified period
        Returns a list of trend alerts
        """
        from datetime import datetime, timedelta
        import pymongo
        
        # Calculate the date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get expenses for the current period
        current_expenses = list(mongo_db.find('expenses', {
            'user_id': user_id,
            'date': {'$gte': start_date, '$lte': end_date}
        }))
        
        # Get expenses for the previous period
        prev_start_date = start_date - timedelta(days=days)
        prev_end_date = start_date
        
        previous_expenses = list(mongo_db.find('expenses', {
            'user_id': user_id,
            'date': {'$gte': prev_start_date, '$lte': prev_end_date}
        }))
        
        # Group expenses by category
        current_by_category = {}
        for expense in current_expenses:
            category = expense.get('category')
            if category not in current_by_category:
                current_by_category[category] = 0
            current_by_category[category] += expense.get('amount', 0)
        
        previous_by_category = {}
        for expense in previous_expenses:
            category = expense.get('category')
            if category not in previous_by_category:
                previous_by_category[category] = 0
            previous_by_category[category] += expense.get('amount', 0)
        
        # Detect significant changes
        alerts = []
        for category, current_amount in current_by_category.items():
            previous_amount = previous_by_category.get(category, 0)
            
            if previous_amount > 0:
                percent_change = ((current_amount - previous_amount) / previous_amount) * 100
                
                if percent_change >= 20:
                    alerts.append({
                        'category': category,
                        'percent_change': round(percent_change),
                        'message': f"Your spending on {category} increased by {round(percent_change)}% in the last {days} days."
                    })
        
        return alerts

