from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.donation_list, name='donations'),
    path('make/', views.make_donation, name='make_donation'),
    path('stripe/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]
