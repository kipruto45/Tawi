import os
import sys
import importlib
import unittest
from pathlib import Path
from django.test.runner import DiscoverRunner


class CustomDiscoverRunner(DiscoverRunner):
    """A small DiscoverRunner that instructs unittest's discover to use the
    project root as the top_level_dir so discovered test modules get fully
    qualified module names (e.g. 'dashboard.tests.test_api') instead of the
    ambiguous 'tests.test_api' which can collide between apps.

    This prevents import-time collisions when multiple apps expose a
    `tests/` package and the default discovery assigns them all to the
    top-level package name 'tests'.
    """

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        # Keep compatibility with parent signature
        test_labels = list(test_labels or [])
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()

        # Project root is two levels up from this file (project package)
        project_root = Path(__file__).resolve().parent.parent

        if not test_labels:
            # No labels: discover from project root
            suite.addTests(loader.discover(start_dir=str(project_root), top_level_dir=str(project_root)))
        else:
            for label in test_labels:
                try:
                    # Try import as an app/module
                    mod = importlib.import_module(label)
                    base = getattr(mod, '__path__', None)
                    if base:
                        start_dir = os.path.join(base[0], 'tests')
                        if os.path.isdir(start_dir):
                            suite.addTests(loader.discover(start_dir=start_dir, top_level_dir=str(project_root)))
                            continue
                except Exception:
                    pass

                # Fallback: let loader discover using label as a dotted module
                try:
                    suite.addTests(loader.loadTestsFromName(label))
                except Exception:
                    # As a last resort, attempt to discover from project root
                    suite.addTests(loader.discover(start_dir=str(project_root), top_level_dir=str(project_root)))

        if extra_tests:
            suite.addTests(extra_tests)

        return suite
