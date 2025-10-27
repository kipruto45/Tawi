"""
Fix role select option values in templates to use canonical role keys from accounts.models.User.ROLE_CHOICES.
This script finds files under templates/ and replaces option value="<label>" with the canonical key when the visible label matches a known role display.
It makes a backup with .bak when modifying a file.
"""
import re
import os
from pathlib import Path

# Load canonical mapping from accounts.models by reading the file
MODEL_PATH = Path('accounts') / 'models.py'
CANONICAL = {}
try:
    text = MODEL_PATH.read_text(encoding='utf-8')
    # crude parse: find ROLE_CHOICES = [ ... ] block and extract tuples
    import ast
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == 'User':
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if getattr(target, 'id', None) == 'ROLE_CHOICES':
                            # evaluate the constant list safely
                            value = ast.literal_eval(stmt.value)
                            for key, label in value:
                                CANONICAL[label.lower()] = key
                                CANONICAL[key.lower()] = key
    if not CANONICAL:
        raise RuntimeError('No ROLE_CHOICES parsed')
except Exception as e:
    # fallback mapping
    CANONICAL = {
        'admin': 'admin',
        'field officer': 'field_officer',
        'field': 'field_officer',
        'partner institution': 'partner',
        'partner': 'partner',
        'partner_institution': 'partner',
        'project manager': 'project_manager',
        'volunteer': 'volunteer',
        'beneficiary': 'beneficiary',
        'guest': 'guest',
        'community': 'community',
    }

print('Canonical mapping samples:', list(CANONICAL.items())[:6])

TEMPLATES_DIR = Path('templates')
pattern = re.compile(r"(<option\s+[^>]*value\s*=\s*\")(?P<val>[^\"]+)(\"[^>]*>\s*(?P<label>[^<]+)\s*</option>)", re.IGNORECASE)

changed_files = []
for p in TEMPLATES_DIR.rglob('*.html'):
    s = p.read_text(encoding='utf-8')
    new = s
    modified = False
    def repl(m):
        val = m.group('val')
        label = m.group('label').strip()
        key = None
        # match label first
        lk = label.lower()
        if lk in CANONICAL:
            key = CANONICAL[lk]
        else:
            # also try val itself (maybe human label used as value already)
            if val.lower() in CANONICAL:
                key = CANONICAL[val.lower()]
        if key and key != val:
            nonlocal_marker = True
            print(f'File {p}: replacing value "{val}" (label "{label}") -> "{key}"')
            return m.group(1) + key + m.group(3)
        return m.group(0)
    # Need to use a function that can access p variable; implement inner
    def repl2(m):
        val = m.group('val')
        label = m.group('label').strip()
        key = None
        lk = label.lower()
        if lk in CANONICAL:
            key = CANONICAL[lk]
        else:
            if val.lower() in CANONICAL:
                key = CANONICAL[val.lower()]
        if key and key != val:
            print(f'File {p}: replacing value "{val}" (label "{label}") -> "{key}"')
            return m.group(1) + key + m.group(3)
        return m.group(0)

    new = pattern.sub(repl2, s)
    if new != s:
        bak = p.with_suffix(p.suffix + '.bak')
        bak.write_text(s, encoding='utf-8')
        p.write_text(new, encoding='utf-8')
        changed_files.append(str(p))

print('Modified files:', changed_files)
if changed_files:
    print('Done. Review changes and commit.')
else:
    print('No changes necessary.')
