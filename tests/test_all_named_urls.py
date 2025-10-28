from django.test import TestCase, Client
from django.urls import get_resolver, reverse, NoReverseMatch


class AllNamedURLsSmokeTest(TestCase):
    """Try reversing all named URL patterns and GET them to ensure no 500s."""

    def setUp(self):
        self.client = Client()

    def _attempt_reverse(self, name):
        # Try several common placeholder kwargs to satisfy converters.
        # Try common placeholders. Order matters: try pk/site_id/uuid first.
        attempts = [
            {},
            {'pk': 1},
            {'pk': '00000000-0000-0000-0000-000000000000'},
            {'site_id': 1},
            {'site': 1},
            {'site_pk': 1},
            {'id': 1},
            {'uuid': '00000000-0000-0000-0000-000000000000'},
            {'slug': 'test'},
            {'uidb64': 'NA', 'token': 'tok'},
        ]
        last_exc = None
        for kw in attempts:
            try:
                return reverse(name, kwargs=kw)
            except NoReverseMatch as exc:
                last_exc = exc
                continue
        raise last_exc or NoReverseMatch(f"Could not reverse {name}")

    def test_all_named_urls_do_not_500(self):
        resolver = get_resolver(None)
        # reverse_dict keys can be bytes or strings; use str()
        names = [k for k in resolver.reverse_dict.keys() if isinstance(k, str)]
        # Some entries in reverse_dict are tuples; filter
        names = [n for n in names if n]

        self.assertTrue(names, 'No named URLs found in project URL resolver')

        for name in sorted(set(names)):
            with self.subTest(url_name=name):
                try:
                    url = self._attempt_reverse(name)
                except Exception as exc:
                    # treat as failure to reverse
                    self.fail(f"Could not reverse URL name '{name}': {exc}")
                # perform GET; we only fail on server errors (5xx)
                resp = self.client.get(url)
                self.assertTrue(resp.status_code < 500, f"URL {url} (name={name}) returned {resp.status_code}")
