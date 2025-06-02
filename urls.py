from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),  # Use custom logout view
    path('profile/', views.profile, name='profile'),
    path('award-badge/<str:badge_name>/', views.award_badge, name='award_badge'),
]


