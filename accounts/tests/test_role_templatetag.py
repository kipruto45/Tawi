from django.test import TestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class RoleTemplateTagTests(TestCase):
    def test_login_and_register_templates_include_canonical_role_options(self):
        """Render the login and register pages and assert every canonical role key
        appears in the rendered HTML as an <option value="key"> entry.
        """
        urls = ['/accounts/login/', '/accounts/register/']
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"{url} did not render")
            html = resp.content.decode('utf-8')
            for key, label in getattr(User, 'CANONICAL_ROLES', getattr(User, 'ROLE_CHOICES', [])):
                # ensure the <option value="key" ...> appears in the HTML
                self.assertIn(f'value="{key}"', html, f"role '{key}' missing from {url}")
