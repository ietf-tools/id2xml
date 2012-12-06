DATABASES = {
    'default' : {
        'ENGINE'   : 'django.db.backends.mysql',
        'NAME'     : 'ietfdb',
        'USER'     : 'ietfdb', 
        'PASSWORD' : 'ing9aGha8Ga0geaj',
        'HOST'     : '/home/mcr/galaxy/orlando/ietfdb/run/mysqld.sock',
        'PORT'     : '',

        'TEST_ENGINE'   : 'django.db.backends.mysql',
        'TEST_NAME'     : 'test_ietfdb',
        'TEST_USER'     : 'test_ietfdb', 
        'TEST_PASSWORD' : 'ing9aGha8Ga0geaj',
        'TEST_HOST'     : '/home/mcr/galaxy/orlando/ietfdb/run/mysqld.sock',
        'TEST_PORT'     : '',
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'poowahmungohvowe'
