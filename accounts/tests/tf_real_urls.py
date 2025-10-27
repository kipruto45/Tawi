from django.urls import path
from two_factor.views import LoginView

app_name = 'two_factor'

urlpatterns = [
    # Map the real two_factor LoginView directly to /account/login/ for testing
    path('account/login/', LoginView.as_view(), name='login'),
]
