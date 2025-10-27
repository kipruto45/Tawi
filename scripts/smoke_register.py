#!/usr/bin/env python3
"""
Simulate a registration POST against the deployed site to verify the flow.
Usage: python .\scripts\smoke_register.py --url https://tawi-lg6j.onrender.com
"""
import sys, argparse, urllib.request, urllib.parse, http.cookiejar, re

def get_csrf(html):
    m = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\'](?P<v>[^"\']+)["\']', html)
    if m:
        return m.group('v')
    m = re.search(r"<input[^>]+name=[\"']csrfmiddlewaretoken[\"'][^>]+value=[\"'](?P<v>[^\"']+)[\"']", html)
    if m:
        return m.group('v')
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', default='https://tawi-lg6j.onrender.com')
    args = p.parse_args()
    base = args.url.rstrip('/')
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPRedirectHandler())
    headers = {'User-Agent': 'smoke-test/1.0'}
    # GET registration page
    req = urllib.request.Request(base + '/accounts/register/', headers=headers)
    try:
        with opener.open(req, timeout=30) as r:
            html = r.read().decode('utf-8')
    except Exception as e:
        print('GET failed:', e)
        sys.exit(2)
    csrf = get_csrf(html)
    print('CSRF token:', csrf)
    # prepare unique username
    import time, uuid
    uname = 'smoketest_' + uuid.uuid4().hex[:8]
    data = {
        'username': uname,
        'email': f'{uname}@example.com',
        'phone': '0700000000',
        'organization': 'Smoke Test Org',
        'county': 'Test County',
        'ward': 'Test Ward',
        'role': 'volunteer',
        'password1': 'Testpass123!',
        'password2': 'Testpass123!',
        'csrfmiddlewaretoken': csrf
    }
    body = urllib.parse.urlencode(data).encode('utf-8')
    post_headers = headers.copy()
    post_headers['Content-Type'] = 'application/x-www-form-urlencoded'
    # include Referer
    post_headers['Referer'] = base + '/accounts/register/'
    req2 = urllib.request.Request(base + '/accounts/register/', data=body, headers=post_headers)
    try:
        with opener.open(req2, timeout=30) as r:
            final_url = r.geturl()
            status = r.getcode()
            resp = r.read().decode('utf-8')
            print('POST result code:', status)
            print('Final URL after POST:', final_url)
            # check messages in resp
            if 'Registration complete' in resp or 'Registration complete' in resp:
                print('Found success text in response')
            # look for login page indicators
            if '/accounts/login/' in final_url or 'Sign In' in resp or 'Sign in' in resp:
                print('Looks like we were redirected to login or login content present')
            # print a short snippet
            print('\n--- Response snippet ---\n')
            print(resp[:2000])
    except urllib.error.HTTPError as e:
        print('POST HTTPError:', e.code)
        try:
            body = e.read().decode('utf-8')
            print(body[:2000])
        except Exception:
            pass
    except Exception as e:
        print('POST failed:', e)

if __name__ == '__main__':
    main()
