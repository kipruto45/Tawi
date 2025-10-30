from django.urls import path
from .views import (
    landing, about, profile, partner_list, message_list, contact,
    # partner placeholders
    partner_add, partner_detail, partner_edit, partner_delete,
)
from .views import terms, privacy
from django.shortcuts import redirect
from .views import message_send, sent_messages

urlpatterns = [
    path('', landing, name='landing'),
    # Convenience access for a public guest landing page
    # Use the top-level alias 'guest_dashboard' which is defined in project urls
    path('guest/', lambda request: redirect('guest_dashboard'), name='guest'),
    path('about/', about, name='about'),
    path('terms/', terms, name='terms'),
    path('privacy/', privacy, name='privacy'),
    path('partners/', partner_list, name='partner_list'),
    # Placeholder CRUD routes for partners used by templates. These currently
    # redirect back to the partner list and act as safe reverses. Replace
    # with real implementations if/when a Partner model is added.
    path('partners/add/', partner_add, name='partner_add'),
    path('partners/<int:pk>/', partner_detail, name='partner_detail'),
    path('partners/<int:pk>/edit/', partner_edit, name='partner_edit'),
    path('partners/<int:pk>/delete/', partner_delete, name='partner_delete'),
    path('messages/', message_list, name='message_list'),
    # Admin helper pages: send messages and view recently sent ones
    path('messages/send/', message_send, name='message_send'),
    path('messages/sent/', sent_messages, name='sent_messages'),
    path('contact/', contact, name='contact'),
    path('profile/', profile, name='profile'),
]
