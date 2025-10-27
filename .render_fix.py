#!/usr/bin/env python3
"""
Simple Render API helper to update a service's startCommand and trigger a deploy.
Usage:
  python .render_fix.py --token <TOKEN> --domain <your-default-domain> --branch <branch> --startcmd "..."

This script uses only the Python stdlib (urllib) so it should run in most environments.
"""
import sys, json, urllib.request, urllib.error, argparse

def req(method, url, token, data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    if data is not None:
        payload = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    else:
        payload = None
    try:
        with urllib.request.urlopen(req, data=payload, timeout=60) as r:
            return r.getcode(), r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8') if e.fp is not None else ''
        return e.code, body
    except Exception as e:
        print('Request error:', e, file=sys.stderr)
        sys.exit(2)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--token', required=True)
    p.add_argument('--domain', required=False, default='tawi-lg6j.onrender.com')
    p.add_argument('--branch', required=False, default='archive-unused-templates-clean')
    p.add_argument('--startcmd', required=False, default='gunicorn tawi_project.wsgi:application --bind 0.0.0.0:$PORT --log-file - --workers 3')
    args = p.parse_args()

    token = args.token
    domain = args.domain
    branch = args.branch
    startcmd = args.startcmd

    print('Listing Render services...')
    status, body = req('GET', 'https://api.render.com/v1/services', token)
    if status >= 400:
        print('Failed to list services:', status, body, file=sys.stderr)
        sys.exit(1)

    services = json.loads(body)
    service = None
    for s in services:
        # look for matching domain fields
        if s.get('defaultDomain') == domain or s.get('defaultCustomDomain') == domain:
            service = s
            break
        # also try matching by domain presence in webServiceUrl or name
        if 'web' in s.get('serviceDetails', {}) or domain in json.dumps(s):
            service = s
            # don't break; prefer exact match

    if service is None and services:
        print('No exact match found for domain; selecting first web service returned by API.')
        service = services[0]

    if service is None:
        print('No services available in this account.', file=sys.stderr)
        sys.exit(1)

    sid = service.get('id')
    sname = service.get('name')
    print(f'Selected service: id={sid} name={sname}')

    print('\nPatching startCommand...')
    status, body = req('PATCH', f'https://api.render.com/v1/services/{sid}', token, data={'startCommand': startcmd})
    print('PATCH status:', status)
    print(body)
    if status >= 400:
        print('Failed to update startCommand. Aborting.', file=sys.stderr)
        sys.exit(1)

    print('\nTriggering deploy for branch:', branch)
    status, body = req('POST', f'https://api.render.com/v1/services/{sid}/deploys', token, data={'branch': branch})
    print('DEPLOY status:', status)
    print(body)
    if status >= 400:
        print('Failed to create deploy.', file=sys.stderr)
        sys.exit(1)

    print('\nDone. Monitor the deploy in Render dashboard or via the API.')

if __name__ == '__main__':
    main()
