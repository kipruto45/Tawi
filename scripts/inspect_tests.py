import os
import sys

# Ensure Django settings are configured
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')

import django
from django.test.runner import DiscoverRunner

# Ensure the project root is on sys.path so importing `tawi_project` works
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

django.setup()

runner = DiscoverRunner(verbosity=1)
labels = ['accounts', 'dashboard']

suite = runner.build_suite(labels)

# Recursively iterate TestSuite to print test ids
from unittest import TestSuite, TestCase

def iter_tests(suite):
    for t in suite:
        if isinstance(t, TestSuite):
            yield from iter_tests(t)
        else:
            yield t

for test in iter_tests(suite):
    try:
        mod_name = getattr(test, '__module__', None)
        mod = sys.modules.get(mod_name)
        mod_file = getattr(mod, '__file__', None) if mod else None
        print(f"id={test.id()} module={mod_name} module_file={mod_file}")
    except Exception as e:
        print(f"<could not get id for {test}: {e}>")

print('\n=== Extra diagnostics ===')
print('tests in sys.modules:', 'tests' in sys.modules)
if 'tests' in sys.modules:
    tmod = sys.modules.get('tests')
    print('tests module:', tmod, getattr(tmod, '__file__', None))

# Try importing specific test module to inspect its assigned module name
try:
    import importlib
    m = importlib.import_module('accounts.tests.test_accounts_api')
    print('imported accounts.tests.test_accounts_api ->', m.__name__, getattr(m, '__file__', None))
    at = importlib.import_module('accounts.tests')
    print('accounts.tests package name:', at.__name__, getattr(at, '__file__', None))
except Exception as e:
    print('Could not import accounts.tests.test_accounts_api:', e)
