#!/usr/bin/env python3
"""
Poll a Render deploy until it finishes and print the first chunk of logs.
Usage: python .poll_deploy.py --token <TOKEN> --deploy <DEPLOY_ID> [--interval 5] [--timeout 600]
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
    p.add_argument('--deploy', required=True)
    p.add_argument('--interval', type=int, default=5)
    p.add_argument('--timeout', type=int, default=600)
    args = p.parse_args()

    token = args.token
    deploy_id = args.deploy
    interval = args.interval
    timeout = args.timeout

    start = time.time()
    print('Polling deploy', deploy_id)
    status = None
    while True:
        code, js = req_json('GET', f'https://api.render.com/v1/deploys/{deploy_id}', token)
        if code >= 400:
            print('Failed to fetch deploy:', code, js)
            sys.exit(1)
        status = js.get('status')
        print('Status:', status, '- updatedAt:', js.get('updatedAt'))
        if status not in ('build_in_progress', 'building', 'queued'):
            break
        if time.time() - start > timeout:
            print('Timed out waiting for deploy to finish')
            break
        time.sleep(interval)

    print('\nFinal status:', status)

    # Attempt to fetch logs for this deploy
    print('\nFetching deploy logs (first 200 lines)...')
    code, body = req_text('GET', f'https://api.render.com/v1/deploys/{deploy_id}/logs', token)
    if code == 200:
        lines = body.splitlines()
        for i, line in enumerate(lines[:200], start=1):
            print(f'{i:04d}: {line}')
        if len(lines) > 200:
            print('\n...truncated, show more with the logs endpoint in the dashboard or increase lines in the script')
    else:
        print('Could not retrieve logs via /v1/deploys/{id}/logs (HTTP', code, ')')
        print('API response/body:', body[:4000])

if __name__ == '__main__':
    main()
