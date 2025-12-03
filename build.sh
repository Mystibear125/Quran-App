#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py ensure_superuser

# Update site domain
python manage.py shell << EOF
from django.contrib.sites.models import Site
import os
try:
    site = Site.objects.get(id=1)
    domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')
    site.domain = domain
    site.name = 'Al-Qur\'an'
    site.save()
    print(f'Site updated: {site.domain}')
except Exception as e:
    print(f'Site update failed: {e}')
EOF