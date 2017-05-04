import os
#: Database backend
SECRET_KEY = 'testkey'
SQLALCHEMY_DATABASE_URI = 'postgres://127.0.0.1/boxoffice_testing'
SERVER_NAME = 'boxoffice.travis.dev:6500'
BASE_URL = 'http://' + SERVER_NAME

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')

ALLOWED_ORIGINS = [BASE_URL, 'http://boxoffice.travis.dev:6500/', 'http://shreyas-wlan.dev:8000']
LASTUSER_SERVER = 'https://auth.hasgeek.com'
LASTUSER_CLIENT_ID = ''
LASTUSER_CLIENT_SECRET = ''
TIMEZONE = 'Asia/Calcutta'
CACHE_TYPE = 'redis'
