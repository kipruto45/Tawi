"""Auto-namespace unambiguous Django template `{% url 'name' %}` usages.

This script:
- Scans all `urls.py` files to build a mapping of route name -> candidate app namespace(s).
- Collects top-level names defined in `tawi_project/urls.py` (these should remain un-prefixed).
- For every template `.html` file, replaces `{% url 'name'` with `{% url 'app:name'` when the name maps
  to exactly one app and is not defined at top-level.

Safety:
- Creates a `.bak` copy of each modified file.
- Only updates unambiguous names (single candidate namespace and not top-level alias).

Run from the repository root: `python scripts/auto_namespace_urls.py`
"""
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]

def find_urls_py_files():
    return list(ROOT.glob('**/urls.py'))

def parse_names_from_urls(path: Path):
    text = path.read_text(encoding='utf-8')
    # find name='something'
    names = re.findall(r"name\s*=\s*'([^']+)'", text)
    return set(names)

def build_name_app_mapping():
    names_to_apps = {}
    top_level_names = set()
    for p in find_urls_py_files():
        rel = p.relative_to(ROOT)
        # treat tawi_project/urls.py as top-level registry
        if rel.parts[0] == 'tawi_project' and p.name == 'urls.py':
            top_level_names |= parse_names_from_urls(p)
            continue
        # skip migrations / virtualenv folders
        if 'migrations' in p.parts:
            continue
        app = p.parent.name
        names = parse_names_from_urls(p)
        for n in names:
            names_to_apps.setdefault(n, set()).add(app)
    return names_to_apps, top_level_names

URL_TAG_RE = re.compile(r"(\{%\s*url\s*')([a-zA-Z0-9_\-]+)(')" )

def process_templates(names_to_apps, top_level_names):
    changed_files = []
    html_files = list(ROOT.glob('**/*.html'))
    for f in html_files:
        try:
            text = f.read_text(encoding='utf-8')
        except Exception:
            continue
        original = text

        def repl(m):
            prefix, name, suffix = m.groups()
            # Skip already namespaced (contains ':') - our pattern won't match those
            if name in top_level_names:
                return m.group(0)
            apps = names_to_apps.get(name)
            if not apps:
                return m.group(0)
            if len(apps) == 1:
                app = list(apps)[0]
                return f"{prefix}{app}:{name}{suffix}"
            # ambiguous mapping - don't change
            return m.group(0)

        new_text = URL_TAG_RE.sub(repl, text)
        if new_text != original:
            bak = f.with_suffix(f.suffix + '.bak')
            shutil.copy2(f, bak)
            f.write_text(new_text, encoding='utf-8')
            changed_files.append(str(f))
    return changed_files

def main():
    names_to_apps, top_level_names = build_name_app_mapping()
    print(f'Found {len(names_to_apps)} named routes across apps and {len(top_level_names)} top-level names')
    # quick stats: ambiguous names
    ambiguous = [n for n,apps in names_to_apps.items() if len(apps) > 1]
    if ambiguous:
        print(f'Warning: {len(ambiguous)} ambiguous route names (won\'t be auto-namespaced):')
        for a in ambiguous[:50]:
            print('  ', a, '->', ','.join(sorted(names_to_apps[a])))
    changed = process_templates(names_to_apps, top_level_names)
    print('Files changed:', len(changed))
    for c in changed:
        print('  ', c)

if __name__ == '__main__':
    main()
