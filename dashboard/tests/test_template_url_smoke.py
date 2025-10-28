import os
import re

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse, NoReverseMatch


class TemplateURLSmokeTests(TestCase):
    """Smoke-test: ensure template {% url 'name' %} tags point to real URLs and don't 500.

    This test only checks simple url tags without arguments, e.g.:
        {% url 'accounts:login' %}

    It will fail if a used name cannot be reversed or if the GET returns a 5xx.
    """

    def setUp(self):
        self.client = Client()

    def test_template_simple_url_tags_resolve_and_respond(self):
        # discover template directories from settings, fallback to <BASE_DIR>/templates
        template_dirs = []
        for tpl in getattr(settings, 'TEMPLATES', []):
            template_dirs.extend(tpl.get('DIRS', []))
        if not template_dirs:
            base = getattr(settings, 'BASE_DIR', None)
            if base:
                template_dirs = [os.path.join(base, 'templates')]

        url_names = set()
        # match simple tags like: {% url 'app:name' %} or {% url "name" %}
        pattern = re.compile(r"{%\s*url\s+['\"]([^'\"]+)['\"]\s*%}")

        for td in template_dirs:
            if not td or not os.path.isdir(td):
                continue
            for root, _, files in os.walk(td):
                for fn in files:
                    if not fn.endswith('.html'):
                        continue
                    path = os.path.join(root, fn)
                    try:
                        text = open(path, encoding='utf-8').read()
                    except Exception:
                        # ignore unreadable files
                        continue
                    for name in pattern.findall(text):
                        url_names.add(name)

        # Sanity: we should find at least some names; otherwise the test might be misconfigured
    # Use f-string and escape braces so literal '{% url "name" %}' is preserved.
    self.assertTrue(url_names, f"No simple {{% url \"name\" %}} tags found in template dirs: {template_dirs}")

        for name in sorted(url_names):
            with self.subTest(url_name=name):
                try:
                    url = reverse(name)
                except NoReverseMatch as exc:
                    self.fail(f"URL name '{name}' used in templates but cannot be reversed: {exc}")
                resp = self.client.get(url)
                # Accept 2xx, 3xx (redirects) and 403 (permission denied) as valid smoke results.
                ok = (resp.status_code < 400) or (resp.status_code == 403)
                self.assertTrue(ok, f"GET {url!s} for '{name}' returned HTTP {resp.status_code}")
