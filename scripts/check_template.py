import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
try:
    import django
    django.setup()
    from django.contrib.staticfiles import finders
except Exception as e:
    print('DJANGO SETUP ERROR:', repr(e))
    sys.exit(2)

logo = finders.find('img/tawi_logo.png')
if logo:
    print('Logo found at', logo)
    sys.exit(0)
else:
    print("Logo not found via staticfiles finders")
    sys.exit(4)
