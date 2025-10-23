import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / 'templates'

form_re = re.compile(r'<form\b[^>]*>(.*?)</form>', re.S | re.I)
csrf_re = re.compile(r'{%\s*csrf_token\s*%}')
load_static_re = re.compile(r'{%\s*load\s+static\s*%}')
extends_base_re = re.compile(r"{%\s*extends\s+['\"](.*base.*\.html)['\"]\s*%}")
url_tag_re = re.compile(r"{%\s*url\s+'([^']+)'")

issues = {
    'forms_missing_csrf': [],
    'missing_load_static': [],
    'non_namespaced_url_tags': [],
    'templates_extending_base': [],
}

for path in TEMPLATES_DIR.rglob('*.html'):
    text = path.read_text(encoding='utf-8')
    rel = path.relative_to(ROOT)

    # check for {% load static %}
    if not load_static_re.search(text):
        # only flag templates that use static tag or extend base (heuristic)
        if 'static' in text or extends_base_re.search(text) or '{% static' in text:
            issues['missing_load_static'].append(str(rel))

    # forms and csrf
    forms = list(form_re.finditer(text))
    for m in forms:
        form_block = m.group(1)
        if not csrf_re.search(form_block):
            issues['forms_missing_csrf'].append(str(rel))
            break

    # url tags without namespace
    for m in url_tag_re.finditer(text):
        name = m.group(1)
        if ':' not in name:
            issues['non_namespaced_url_tags'].append((str(rel), name))

    # templates that extend base
    if extends_base_re.search(text):
        issues['templates_extending_base'].append(str(rel))

# Deduplicate
issues['forms_missing_csrf'] = sorted(set(issues['forms_missing_csrf']))
issues['missing_load_static'] = sorted(set(issues['missing_load_static']))
issues['non_namespaced_url_tags'] = sorted(set(issues['non_namespaced_url_tags']))
issues['templates_extending_base'] = sorted(set(issues['templates_extending_base']))

print('Template scan report')
print('====================')
print('\nForms missing {% csrf_token %}:')
for p in issues['forms_missing_csrf']:
    print(' -', p)

print('\nTemplates missing "{% load static %}" (but using static or extending base):')
for p in issues['missing_load_static']:
    print(' -', p)

print('\nURL tags without namespace (template, name):')
for p, name in issues['non_namespaced_url_tags']:
    print(' -', p, name)

print('\nTemplates that extend a base template:')
for p in issues['templates_extending_base']:
    print(' -', p)

# Summary
print('\nSummary:')
for k, v in issues.items():
    print(f' {k}:', len(v))
