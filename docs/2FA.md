# Two-Factor Authentication (2FA) — Enabling Guide

This project contains optional support for two-factor authentication using `django-two-factor-auth` and `django-otp`. The codebase wires the `two_factor` URLs only when the package and its dependencies are installed so missing optional packages will not break startup.

Quick enable steps

1. Install the optional dependencies (recommended to pin versions):

   ```powershell
   .venv\Scripts\activate
   pip install django-two-factor-auth django-otp qrcode
   pip install -r requirements.txt
   ```

2. Enable 2FA in settings by exporting the env var used in `settings.py`:

   - Locally (PowerShell):
     ```powershell
     $Env:USE_2FA = "1"
     python manage.py migrate
     python manage.py runserver
     ```

   - On Render (or other hosts): set the environment variable `USE_2FA=1` in the service's environment settings, then redeploy.

3. Apply migrations to create tables required by `django_otp` and `two_factor`:

   ```powershell
   python manage.py migrate
   ```

4. Visit the 2FA setup pages:

   - The two-factor flows are mounted under `/account/` when enabled. Examples:
     - `/account/login/` — login flow (if you want to use the package's login views)
     - `/account/profile/two_factor/` and related setup pages for TOTP devices

Optional: make the site's primary login route use the two-factor login view
----------------------------------------------------------------------

If you prefer users to always go through the two-factor login flow when
`USE_2FA` is enabled, this project includes a small convenience: when
`USE_2FA=1` and `django-two-factor-auth` is installed, the project's
`accounts` URL configuration will automatically swap the `accounts:login`
route to point at `two_factor.views.LoginView`. This means existing links
to `{% url 'accounts:login' %}` will route users through the 2FA flow
without changing templates.

Notes:

- Make sure the package is installed in the environment running the
   project (Render, local venv) before enabling `USE_2FA` or the app
   discovery will skip the swap (safe fallback).
- If you want stronger control (for example, to keep the custom login
   view and explicitly redirect to 2FA only for certain users), I can
   implement a middleware or a small view wrapper that redirects to the
   two-factor login conditionally based on user attributes.

Notes and tips

- The project intentionally mounts two-factor routes only when the packages are installed so tests and minimal deploys without these optional packages continue to function.

- If you want the project to always use the two-factor login flow, consider updating `LOGIN_URL`/login view wiring to use `two_factor.views.LoginView` or adjust the `accounts` app to delegate to the two-factor login view.

- After enabling 2FA in production, test thoroughly with a non-admin account and ensure email/SMS providers (if used) are configured and working.

- If you need help wiring the two-factor views more tightly into the `accounts` login flow (e.g., single-sign-on between `accounts:login` and the 2FA flow), tell me and I can implement the redirection or view subclassing.
