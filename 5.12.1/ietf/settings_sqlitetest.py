# Standard settings except we use SQLite, this is useful for speeding
# up tests that depend on the test database, try for instance:
#
#   ./manage.py test --settings=settings_sqlitetest doc.ChangeStateTestCase
#

from settings import *                  # pyflakes:ignore

DATABASES = {
    'default': {
        'NAME': 'test.db',
        'ENGINE': 'django.db.backends.sqlite3',
        },
    }

MIGRATION_MODULES = {"liaisons": "liaisons.migrations_not_used_in_tests"}
