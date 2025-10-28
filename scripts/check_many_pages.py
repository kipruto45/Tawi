#!/usr/bin/env python
"""Check a set of common pages via Django test client and print status and exceptions."""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
import django
django.setup()
from django.test import Client

client = Client()
urls = [
    '/',
    '/accounts/login/',
    '/accounts/register/',
    '/dashboard/',
    '/accounts/profile/',
    '/donations/',
    '/reports/',
    '/trees/',
    '/trees/planted/',
    '/upcoming-events/',
    '/locations/',
    '/feedback/',
    '/notifications/',
]

for u in urls:
    try:
        resp = client.get(u)
        print(f"GET {u} -> status {resp.status_code}")
        if resp.status_code >= 500:
            print('Response content (truncated):')
            print(resp.content[:2000])
    except Exception as e:
        print(f"GET {u} -> exception: {type(e).__name__}: {e}")
