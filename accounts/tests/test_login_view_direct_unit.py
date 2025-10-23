from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

from accounts.views import CustomLoginView


class DirectFormValidTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username='direct_user', password='pw12345', role='volunteer')
        self.factory = RequestFactory()

    def _attach_middleware(self, request):
        # SessionMiddleware and MessageMiddleware require a get_response callable
        SessionMiddleware(lambda r: None).process_request(request)
        request.session.save()
        MessageMiddleware(lambda r: None).process_request(request)

    def test_form_valid_respects_post_next(self):
        """Directly calling CustomLoginView.form_valid should respect an explicit POST 'next'."""
        login_path = reverse('login')
        target = reverse('dashboard_field')

        request = self.factory.post(login_path, {'next': target})
        request.user = AnonymousUser()
        self._attach_middleware(request)

        # Ensure the user object has a backend attribute so auth_login won't raise
        # (auth_login expects user.backend or session backend key to be set).
        setattr(self.user, 'backend', 'django.contrib.auth.backends.ModelBackend')

        view = CustomLoginView()
        view.request = request
        view.kwargs = {}

        class DummyForm:
            def get_user(inner):
                return self.user

        form = DummyForm()

        response = view.form_valid(form)

        self.assertIn(response.status_code, (301, 302))
        loc = response.get('Location', '')
        self.assertTrue(loc.endswith(target), msg=f"Expected explicit next to be used, got {loc!r}")
