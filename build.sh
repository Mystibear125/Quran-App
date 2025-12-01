#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py ensure_superuser

# Update site domain for production
python manage.py shell << EOF
from django.contrib.sites.models import Site
try:
    site = Site.objects.get(id=1)
    site.domain = 'quran-app-7jbw.onrender.com'
    site.name = 'Al-Qur\'an'
    site.save()
    print(f'Site updated: {site.domain}')
except Exception as e:
    print(f'Site update failed: {e}')
EOF