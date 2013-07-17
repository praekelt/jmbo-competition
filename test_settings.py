from foundry.settings import *


# We cannot use ssqlite or spatialite because it cannot handle the 'distinct'
# in admin.py.
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'competition',
        'USER': 'test',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SOUTH_TESTS_MIGRATE = False
