# Enabling Google Sign-in (django-allauth)

This project has optional support for social login via `django-allauth`.
Follow these steps to enable Google Sign-In locally or in your deployment.

1) Install required packages (activate your virtualenv first):

```powershell
pip install django-allauth dj-rest-auth
```

2) Enable allauth in your environment by setting the environment variable:

```powershell
setx USE_ALLAUTH 1
```

Or on Linux/macOS:

```bash
export USE_ALLAUTH=1
```

3) Provide Google OAuth credentials as environment variables:

- `GOOGLE_CLIENT_ID` - OAuth client ID from Google Cloud Console
- `GOOGLE_SECRET` - OAuth client secret
- `SITE_ID` - Django `Site` record id (default 1)

4) In Google Cloud Console make sure to add the OAuth redirect URI:

```
http://localhost:8000/accounts/google/login/callback/
```

5) Restart the Django dev server. When `USE_ALLAUTH` is enabled the login
   template will show a "Sign in with Google" button that uses django-allauth's
   provider URL (`{% provider_login_url 'google' %}`).

Notes:
- You may want to configure `ACCOUNT_EMAIL_VERIFICATION` and other account
  settings via environment variables for production.
- For production, use HTTPS redirect URIs and restrict origins in Google Cloud.
