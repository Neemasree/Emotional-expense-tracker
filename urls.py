from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('list/', views.expense_list, name='expense_list'),
    path('add/', views.add_expense, name='add_expense'),
    path('analytics/', views.expense_analytics, name='expense_analytics'),
    path('challenges/create/', views.create_challenge, name='create_challenge'),
    path('challenges/complete/<str:challenge_id>/', views.complete_challenge, name='complete_challenge'),
    path('predict-regret/', views.predict_regret, name='predict_regret'),
    path('trigger-habits/', views.trigger_habits, name='trigger_habits'),
]





