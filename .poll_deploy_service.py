#!/usr/bin/env python3
"""
Poll a Render deploy via the service deploys list and print logs.
Usage: python .poll_deploy_service.py --token <TOKEN> --service <SERVICE_ID> --deploy <DEPLOY_ID>
"""
import sys, time, json, argparse, urllib.request, urllib.error

def req_json(method, url, token, data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    if data is not None:
        payload = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    else:
        payload = None
    try:
        with urllib.request.urlopen(req, data=payload, timeout=60) as r:
            return r.getcode(), json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8') if e.fp is not None else ''
        return e.code, {'error': body}
    except Exception as e:
        print('Request error:', e, file=sys.stderr)
        sys.exit(2)


def req_text(method, url, token):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.getcode(), r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8') if e.fp is not None else ''
        return e.code, body
    except Exception as e:
        return 0, str(e)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--token', required=True)
    p.add_argument('--service', required=True)
    p.add_argument('--deploy', required=True)
    p.add_argument('--interval', type=int, default=5)
    p.add_argument('--timeout', type=int, default=900)
    args = p.parse_args()

    token = args.token
    service = args.service
    deploy_id = args.deploy
    interval = args.interval
    timeout = args.timeout

    start = time.time()
    print('Polling deploy', deploy_id, 'for service', service)
    status = None
    in_progress_states = {'build_in_progress','building','queued','update_in_progress'}
    while True:
        code, js = req_json('GET', f'https://api.render.com/v1/services/{service}/deploys', token)
        if code >= 400:
            print('Failed to fetch service deploys:', code, js)
            sys.exit(1)
        # js is a list of deploy entries
        found = None
        for item in js:
            d = item.get('deploy') or item
            if d.get('id') == deploy_id:
                found = d
                break
        if not found:
            print('Deploy id not found in service deploys; will retry...')
        else:
            status = found.get('status')
            print('Status:', status, 'createdAt:', found.get('createdAt'), 'updatedAt:', found.get('updatedAt'))
            if status not in in_progress_states:
                break
        if time.time() - start > timeout:
            print('Timed out waiting for deploy to finish')
            break
        time.sleep(interval)

    print('\nFinal status:', status)

    # Attempt to fetch logs. Try deploy logs endpoint first, then service deploys logs path
    tried = []
    for url in (
        f'https://api.render.com/v1/deploys/{deploy_id}/logs',
        f'https://api.render.com/v1/services/{service}/deploys/{deploy_id}/logs',
    ):
        tried.append(url)
        code, body = req_text('GET', url, token)
        if code == 200:
            print('\nFetched logs from', url)
            lines = body.splitlines()
            for i, line in enumerate(lines[:200], start=1):
                print(f'{i:04d}: {line}')
            if len(lines) > 200:
                print('\n...truncated (show more with the dashboard or increase lines)')
            return
        else:
            print('\nAttempt to fetch logs from', url, 'failed HTTP', code)
    print('\nAll log endpoints failed. Last response body (truncated):')
    print(body[:4000])

if __name__ == '__main__':
    main()
