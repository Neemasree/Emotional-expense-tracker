from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import redirect

# Simple view for the root URL
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return HttpResponse("<h1>Welcome to Emotional Expense Tracker</h1><p>Please <a href='/users/login/'>login</a> or <a href='/users/register/'>register</a> to continue.</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Add a simple home view
    path('expenses/', include('expenses.urls')),
    path('users/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


