#!/usr/bin/env python
"""Simple script to GET common pages using Django test client and report status.
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
import django
django.setup()
from django.test import Client

client = Client()
urls = ['/', '/accounts/login/']

for u in urls:
    try:
        resp = client.get(u)
        print(f"GET {u} -> status {resp.status_code}")
        if resp.status_code >= 500:
            print('Response content (truncated):')
            print(resp.content[:200])
    except Exception as e:
        print(f"GET {u} -> exception: {type(e).__name__}: {e}")
