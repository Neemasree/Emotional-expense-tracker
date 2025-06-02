from django import forms
from .models import TriggerHabit
from db_connector import MongoDBConnector

# Initialize MongoDB connector
mongo_db = MongoDBConnector()

class ExpenseForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )
    
    category = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    REGRET_CHOICES = [
        ('essential', 'Essential'),
        ('treat', 'Treat'),
        ('impulse', 'Impulse'),
        ('regretted', 'Regretted'),
    ]
    
    regret_level = forms.ChoiceField(
        choices=REGRET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get trigger habits from MongoDB
        trigger_habits = list(mongo_db.find('trigger_habits'))
        
        # Create MultipleChoiceField for trigger habits
        self.fields['trigger_habits'] = forms.MultipleChoiceField(
            choices=[(habit['name'], habit['name']) for habit in trigger_habits],
            widget=forms.CheckboxSelectMultiple(),
            required=False
        )

class ChallengeForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )
    
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    
    points_reward = forms.IntegerField(
        initial=10,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )



