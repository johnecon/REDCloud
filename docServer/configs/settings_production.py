DEBUG = False
TEMPLATE_DEBUG = False
REQUIRE_DEBUG = False
ALLOWED_HOSTS = ['redcloud.compute.dtu.dk']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': 'db',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'redis:6379',
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 150,
                'timeout': 20,
            }
        },
    },
}