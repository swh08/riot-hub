#!/bin/bash

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Checking superuser..."
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  echo "Creating superuser: $DJANGO_SUPERUSER_USERNAME"
  python manage.py createsuperuser \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL" \
    --noinput || true

  echo "Setting superuser password..."
  python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    user = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME')
    user.set_password('$DJANGO_SUPERUSER_PASSWORD')
    user.save()
    print('Superuser password has been set')
except User.DoesNotExist:
    print('Superuser does not exist')
except Exception as e:
    print('Error while setting password:', str(e))
"
else
  echo "Superuser environment variables are not set, skipping superuser creation"
fi

echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 config.wsgi:application
