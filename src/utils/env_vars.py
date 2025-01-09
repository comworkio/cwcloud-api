import os

DOMAIN = os.getenv('DOMAIN', 'http://localhost:3000')
APP_VERSION = os.getenv('APP_VERSION', '1.0')
APP_ENV = os.getenv('APP_ENV', 'local')
