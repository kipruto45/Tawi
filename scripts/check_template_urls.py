#!/usr/bin/env python3
"""Scan templates for `{% url ... %}` usages and check whether the named URL exists in project urls.py files.

Usage: python scripts/check_template_urls.py
"""
import re
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / 'templates'

url_pattern = re.compile(r"{%\s*url\s+['\"]([^'\"]+)['\"]")
name_pattern = re.compile(r"name\s*=\s*['\"]([^'\"]+)['\"]")
app_name_pattern = re.compile(r"app_name\s*=\s*['\"]([^'\"]+)['\"]")


def find_template_urls():
    found = set()
    if not TEMPLATES_DIR.exists():
        return found
    for p in TEMPLATES_DIR.rglob('*.html'):
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        for m in url_pattern.finditer(text):
            found.add((str(p.relative_to(ROOT)), m.group(1)))
    return found


def find_url_names():
    """Return global names set and a mapping of app_name -> set(names) found in urls.py files."""
    global_names = set()
    apps = {}
    for p in ROOT.rglob('urls.py'):
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        # find app_name if present
        app_name = None
        m = app_name_pattern.search(text)
        if m:
            app_name = m.group(1)
        # find all name='...'
        names = set(name_pattern.findall(text))
        if app_name:
            apps.setdefault(app_name, set()).update(names)
        # also treat names as global since include() may wire them
        global_names.update(names)
    return global_names, apps


def main():
    tmpl_urls = find_template_urls()
    global_names, apps = find_url_names()

    print(f"Scanned {len(tmpl_urls)} template url usages.")

    missing = []
    for tpl, ref in sorted(tmpl_urls):
        if ':' in ref:
            ns, nm = ref.split(':', 1)
            if ns in apps and nm in apps[ns]:
                continue
            # fallback: check global names too
            if nm in global_names:
                continue
            missing.append((tpl, ref))
        else:
            if ref in global_names:
                continue
            missing.append((tpl, ref))

    if not missing:
        print('No missing URL names detected.')
        return 0

    print('\nMissing URL names detected:')
    for tpl, ref in missing:
        print(f" - {tpl}: {ref}")
    print('\nRecommendation: add matching `path(..., name=\"{name}\")` entries in the appropriate `urls.py` or adjust template links to the correct namespaced name.')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
