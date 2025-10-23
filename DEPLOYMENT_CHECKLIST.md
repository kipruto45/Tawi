Tawi Tree Planting - Render Deployment Checklist

1) Set secrets in Render dashboard
   - SECRET_KEY: generate a secure value (use scripts/generate_secret.py)
   - DJANGO_DEBUG=False
   - ALLOWED_HOSTS=.your-app.onrender.com
   - DATABASE_URL: set from Render Postgres service
   - EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT, EMAIL_USE_TLS
   - OPTIONAL: S3 credentials if USE_S3=1

2) Requirements & runtime
   - Ensure `requirements.txt` is present and up-to-date (contains gunicorn, dj-database-url, psycopg2-binary, whitenoise)
   - runtime.txt must specify the Python version (e.g. python-3.11.16)

3) Static files
   - In Render, the build step should run: `python -m pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Ensure `STATIC_ROOT` is set (project already sets it to `BASE_DIR/staticfiles`)
   - If using Whitenoise, STATICFILES_STORAGE should be set to `whitenoise.storage.CompressedManifestStaticFilesStorage`

4) Database migrations
   - After the service starts, run `python manage.py migrate` (Render allows one-off commands)

5) Health checks & logs
   - Add a health check route (e.g. `/`) or use Render's HTTP checks pointed at the root
   - Monitor the logs for errors during startup (migrations, collectstatic, missing env vars)

6) Email test
   - Use Django shell or a simple management command to send a test email and verify SMTP settings work.

7) Security checks
   - Run `python manage.py check --deploy` with DJANGO_DEBUG=False to ensure common production settings are correct
   - Set SECURE_SSL_REDIRECT=True and HSTS settings only if you intend to enforce HTTPS

8) Post-deploy
   - Run smoke tests covering login, registration, and key API endpoints
   - Monitor error tracking (Sentry) and background jobs (Celery + Redis) if used

Notes:
- Do not commit `.env` with production values. Keep `.env.example` as a template.
- Use Render's environment variable UI to provide secrets.
