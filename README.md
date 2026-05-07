# Attendance
Python Case Study

## Render Deployment

This project is configured for Render with `render.yaml`.

Render will:

- install packages from `requirements.txt`
- collect static files with WhiteNoise
- run database migrations on startup
- start the app with Gunicorn
- create a Postgres database and provide `DATABASE_URL`

If you deploy manually instead of using the blueprint, set these environment variables:

- `SECRET_KEY`: a long random Django secret key
- `DEBUG`: `False`
- `DATABASE_URL`: your Render Postgres internal connection string
- `ALLOWED_HOSTS`: your Render hostname, for example `your-app.onrender.com`

Use this start command on Render:

```bash
python manage.py migrate && gunicorn AttendanceSystem.wsgi:application
```
