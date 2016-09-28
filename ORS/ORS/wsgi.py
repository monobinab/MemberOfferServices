"""
WSGI config for ORS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

# add the hellodjango project path into the sys.path
sys.path.append('/home/affine/Projects/ORS/')


# add the virtualenv site-packages path to the sys.path
sys.path.append('/home/affine/Projects/ORS/Lib/')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ORS.settings")

application = get_wsgi_application()
