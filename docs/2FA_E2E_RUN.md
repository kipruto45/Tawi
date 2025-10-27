Running the 2FA E2E test (local and CI)

This project contains a single E2E test exercising the email-based 2FA login flow:

- Test: `accounts.tests.test_2fa_wizard_e2e.TwoFactorWizardE2ETest`

Local (Windows PowerShell)

1. Activate your virtualenv and install dependencies (if not already done):

```powershell
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

2. Ensure migrations are applied (recommended):

```powershell
$env:USE_2FA = '1'
python manage.py migrate --noinput
```

3. Run the single E2E test:

```powershell
$env:USE_2FA = '1'
python manage.py test accounts.tests.test_2fa_wizard_e2e -v 2
```

Notes:
- The fast E2E test uses `override_settings(ROOT_URLCONF='accounts.tests.tf_test_urls', USE_2FA=True, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')` and a small test-only login view at `accounts/tests/tf_test_urls.py`. That test is self-contained and is intended for quick feedback.
- The repository also includes a "real" E2E test (`accounts.tests.test_2fa_wizard_e2e_real`) which exercises the actual `two_factor` LoginView. To keep local developer runs reliable, the real test will automatically fall back to the lightweight test view if required OTP device tables are missing in the test DB. When the fallback happens the test logs a warning explaining why.

CI (GitHub Actions)

- The workflow `.github/workflows/2fa-e2e.yml` contains two jobs:
	- `e2e-2fa`: fast, lightweight job that uses the test-only login view (quick feedback)
	- `e2e-2fa-real`: slower, full-fidelity job that runs the real `two_factor` LoginView against a Postgres service with migrations applied. This job is configured to run after the fast job.

Recommendations:
- Keep both CI jobs: the fast job gives immediate feedback for most changes; the real job verifies integration with the actual `two_factor`/`django_otp` stack.
- If you want to run the real test locally, use a Postgres instance and run migrations before the test (this mirrors CI closely):

```powershell
$env:USE_2FA = '1'
# point DATABASE_URL to a local Postgres if your settings use it
python manage.py migrate --noinput
$env:USE_2FA = '1'
python manage.py test accounts.tests.test_2fa_wizard_e2e_real -v 2
```

If the real test falls back locally, you'll see a logged warning and the test will exercise the lightweight flow instead. This keeps developer runs fast and reliable while CI still checks the full integration.

Postgres local/CI parity

If you want your local development/test runs to use Postgres (matching CI), set the `USE_POSTGRES` environment variable and provide the `POSTGRES_*` vars or a `DATABASE_URL`. Example (PowerShell) to run a local Postgres-backed migration and the real E2E test:

```powershell
$env:USE_POSTGRES = '1'
$env:POSTGRES_DB = 'tawi_db'
$env:POSTGRES_USER = 'postgres'
$env:POSTGRES_PASSWORD = '<your-postgres-password>'
$env:POSTGRES_HOST = '127.0.0.1'
$env:POSTGRES_PORT = '5432'
$env:USE_2FA = '1'
python manage.py migrate --noinput
python manage.py test accounts.tests.test_2fa_wizard_e2e_real -v 2
```

Controlling the Django test database name

By default Django creates a test database named `test_<DBNAME>`. To make
local test runs predictable and match CI, the project supports setting the
`DJANGO_TEST_DB_NAME` environment variable which will be used as
`DATABASES['default']['TEST']['NAME']` when present.

Example (PowerShell) — pre-create and reuse a test DB called `test_tawi_db`:

```powershell
$env:DJANGO_TEST_DB_NAME = 'test_tawi_db'
$env:DATABASE_URL = 'postgres://postgres:<your-postgres-password>@127.0.0.1:5432/test_tawi_db'
# apply migrations to the test DB once
python manage.py migrate --noinput
# run the strict Postgres-backed tests while preserving the DB
python manage.py test accounts.tests.test_2fa_wizard_e2e_real accounts.tests.test_2fa_integration_real_strict -v 2 --keepdb
```

In CI we already set `DATABASE_URL` / run a Postgres service and run `migrate --noinput` before tests, so the strict Postgres-only integration test will run there.

Local helper: send a 2FA test email via management command

You can trigger a test 2FA email (helpful for manual verification) with the new management command `send_2fa_test_email`.

Examples (PowerShell):

```powershell
$env:USE_2FA = '1'
python manage.py send_2fa_test_email tawiproject@gmail.com --create
```

Output notes:
- The command will print the `EMAIL_BACKEND` value. Locally we recommend using `django.core.mail.backends.locmem.EmailBackend` so the message is captured in `django.core.mail.outbox` and printed to the console for quick inspection.
- If no `EmailDevice` exists for the user, `--create` will create one (confirmed) pointing at the user's email.
