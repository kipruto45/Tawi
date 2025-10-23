#!/usr/bin/env python3
"""Generate a secure Django SECRET_KEY for use in environment variables."""
import secrets
import sys

def generate(length=50):
    # Django's default secret key length is 50
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == '__main__':
    key = generate()
    print(key)
    sys.exit(0)
