import re
from pathlib import Path
import os

# Ensure Django settings are available
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
import django
django.setup()

from django.urls import reverse, NoReverseMatch

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / 'templates'

url_tag_re = re.compile(r"{%\s*url\s+'([^']+)'")

# Known app namespaces to try (conservative list)
app_namespaces = ['accounts', 'dashboard', 'core', 'media_app', 'reports', 'donations', 'beneficiaries', 'trees', 'monitoring', 'notifications', 'qrcodes', 'feedback', 'events']

suggestions = []

for path in TEMPLATES_DIR.rglob('*.html'):
    text = path.read_text(encoding='utf-8')
    rel = path.relative_to(ROOT)
    for m in url_tag_re.finditer(text):
        name = m.group(1)
        if ':' in name:
            continue
        # Try resolve un-namespaced
        try:
            reverse(name)
            # If this works, it's fine
            continue
        except Exception:
            pass

        found = []
        for ns in app_namespaces:
            try:
                reverse(f"{ns}:{name}")
                found.append(f"{ns}:{name}")
            except Exception:
                pass

        suggestions.append((str(rel), name, found))

# Print report
print('Namespace suggestion report')
print('===========================')
for tpl, name, found in suggestions:
    if found:
        print(f"{tpl}: '{name}' -> suggested: {', '.join(found)}")
    else:
        print(f"{tpl}: '{name}' -> no namespace suggestion found (requires manual review)")

print('\nSummary: total occurrences scanned:', len(suggestions))
