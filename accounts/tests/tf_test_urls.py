from django.urls import path
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect

# Test-only lightweight two-step login flow used by the E2E test. This
# avoids invoking the real two_factor wizard and any django_otp device
# enumeration, making the test self-contained while preserving the
# behavior the E2E test expects: a POST of credentials that sends an
# email with a numeric token, then a token POST that authenticates the
# user.

app_name = 'two_factor'

def _render_form(token_step=False):
    # Minimal HTML with some hidden inputs the test picks up. When
    # token_step=True we render a token entry form, otherwise the
    # credential form.
    if token_step:
        return HttpResponse('\n'.join([
            '<html><body>',
            '<form method="post">',
            '<input type="hidden" name="wizard-current_step" value="token" />',
            '<input type="text" name="token" />',
            '<input type="submit" value="Submit token" />',
            '</form>',
            '</body></html>'
        ]))
    return HttpResponse('\n'.join([
        '<html><body>',
        '<form method="post">',
        '<input type="hidden" name="wizard-current_step" value="auth" />',
        '<input type="text" name="auth-username" />',
        '<input type="password" name="auth-password" />',
        '<input type="submit" value="Login" />',
        '</form>',
        '</body></html>'
    ]))

def login_view(request):
    User = get_user_model()
    if request.method == 'GET':
        return _render_form(token_step=False)

    # POST handling
    if 'auth-username' in request.POST:
        username = request.POST.get('auth-username')
        password = request.POST.get('auth-password')
        user = authenticate(username=username, password=password)
        if user is None:
            return _render_form(token_step=False)

        # generate a simple numeric token and store in session
        import random
        token = f"{random.randint(100000, 999999)}"
        request.session['__test_2fa_token'] = token
        request.session['__test_2fa_user'] = user.pk

        # send email via Django's email backends (captured in locmem outbox)
        send_mail('Your token', f'Your token is: {token}', 'no-reply@example.com', [user.email])
        return _render_form(token_step=True)

    if 'token' in request.POST:
        entered = request.POST.get('token')
        token = request.session.get('__test_2fa_token')
        user_pk = request.session.get('__test_2fa_user')
        if token and entered == token and user_pk:
            try:
                user = User.objects.get(pk=user_pk)
                auth_login(request, user)
                return HttpResponse('OK')
            except User.DoesNotExist:
                pass
        return _render_form(token_step=True)

    return _render_form(token_step=False)


urlpatterns = [
    path('account/login/', login_view, name='login'),
]
