Render deployment checklist

1) Add the repo to Render and create a new Web Service (Python environment).

2) Set environment variables (in Render: Dashboard > Service > Environment):
   - SECRET_KEY: a secure random value
   - DJANGO_DEBUG: False
   - ALLOWED_HOSTS: .your-app.onrender.com,yourdomain.com
   - DATABASE_URL: (Render's managed Postgres) or your DATABASE URL
   - EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
   - EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
   - DEFAULT_FROM_EMAIL and SERVER_EMAIL default to tawiproject@gmail.com but can be changed.
   - STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET (if using Stripe)
   - USE_S3 and AWS_* envs if using S3 for media
   - CELERY_BROKER_URL and CELERY_RESULT_BACKEND if running Celery workers

3) Build & start commands
   - Build command (Render): pip install -r requirements.txt && python manage.py collectstatic --noinput
   - Start command (Procfile or Render startCommand): gunicorn tawi_project.wsgi --log-file - --workers 3

4) Database migrations
   - After deploy, run: python manage.py migrate

5) Optional: set up background workers for Celery (if used)

6) Monitoring & logs
   - Render gives you service logs; configure external logging for long-term retention.

Quick local smoke test (run in your virtualenv):

```powershell
pip install -r requirements.txt
python manage.py check
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py runserver
```

Notes
- Settings are environment-driven; the project defaults to console email backend locally. For production, set SMTP envs.
- I added WhiteNoise support; install `whitenoise` in production (it's already in requirements.txt) so static files are served.
- If you prefer automatic DATABASE parsing, consider adding `dj-database-url` and using it instead of the simple parser here.
*** End Patch