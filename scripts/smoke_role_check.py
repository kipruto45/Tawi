#!/usr/bin/env python3
"""Simple smoke tester for the /accounts/api/role_check/ endpoint.

Usage: python scripts/smoke_role_check.py --url https://example.com/accounts/api/role_check/ \
       --username jdoe --role volunteer

This script sends a JSON POST and prints the response.
"""
import argparse
import requests
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', required=True)
    p.add_argument('--username', required=True)
    p.add_argument('--role', required=False, default='')
    p.add_argument('--csrftoken', required=False, help='Optional CSRF token to send in X-CSRFToken header')
    args = p.parse_args()

    headers = {'Content-Type': 'application/json'}
    if args.csrftoken:
        headers['X-CSRFToken'] = args.csrftoken

    payload = {'username': args.username, 'role': args.role}

    try:
        r = requests.post(args.url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print('Request failed:', e)
        sys.exit(2)

    print('Status:', r.status_code)
    try:
        print('JSON:', r.json())
    except Exception:
        print('Body:', r.text)


if __name__ == '__main__':
    main()
