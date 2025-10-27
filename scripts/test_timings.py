#!/usr/bin/env python
"""Run Django tests while measuring per-test durations.

This script uses Django's DiscoverRunner to set up databases, then runs
unittest discovery with a custom result class that times each test. After
the run it prints the slowest tests.

Usage (recommended in CI):
  python scripts/test_timings.py --top 20

Note: this requires the environment to be configured (DJANGO_SETTINGS_MODULE,
POSTGRES_* or DATABASE_URL). Running locally may require a pre-created test DB
or using --keepdb behavior via environment.
"""
import time
import argparse
import unittest
from collections import defaultdict

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
import django
django.setup()

from django.test.runner import DiscoverRunner


class TimingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_time = None
        self.test_times = {}

    def startTest(self, test):
        self._start_time = time.time()
        super().startTest(test)

    def stopTest(self, test):
        elapsed = time.time() - (self._start_time or time.time())
        self.test_times[str(test)] = elapsed
        super().stopTest(test)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--top', type=int, default=20, help='Show top N slowest tests')
    parser.add_argument('labels', nargs='*', help='Optional test labels to run')
    args = parser.parse_args()

    runner = DiscoverRunner(verbosity=1, keepdb=True)
    old_config = runner.setup_databases()
    loader = unittest.TestLoader()
    if args.labels:
        # Build suite for given labels
        suite = loader.loadTestsFromNames(args.labels)
    else:
        suite = loader.discover('.')

    text_runner = unittest.TextTestRunner(verbosity=2, resultclass=TimingResult)
    result = text_runner.run(suite)

    # Print summary of slowest tests
    times = getattr(result, 'test_times', {})
    if times:
        sorted_times = sorted(times.items(), key=lambda kv: kv[1], reverse=True)
        print('\nSlowest tests:')
        for i, (test_name, secs) in enumerate(sorted_times[: args.top]):
            print(f"{i+1:2d}. {secs:.3f}s  {test_name}")
    else:
        print('\nNo timing information captured.')

    runner.teardown_databases(old_config)


if __name__ == '__main__':
    main()
