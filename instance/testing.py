import os
#: Database backend
SECRET_KEY = 'testkey'
# SQLALCHEMY_DATABASE_URI = 'postgres://127.0.0.1/boxoffice_testing'
# SQLALCHEMY_DATABASE_URI = 'postgresql://dev:dev@localhost:5434/boxoffice_testing'
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:pg@localhost:5433/boxoffice_testing'
SERVER_NAME = 'shreyas-wlan.dev:6500'
BASE_URL = 'http://' + SERVER_NAME

# RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
# RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
RAZORPAY_KEY_ID = 'rzp_test_Q9IkZPcoEYzfv9'
RAZORPAY_KEY_SECRET = 'Z384nK5tumwzknlf2QtxX4L5'

ALLOWED_ORIGINS = [BASE_URL, 'http://boxoffice.travis.dev:6500/', 'http://shreyas-wlan.dev:8000']
LASTUSER_SERVER = 'https://auth.hasgeek.com'
LASTUSER_CLIENT_ID = ''
LASTUSER_CLIENT_SECRET = ''
TIMEZONE = 'Asia/Calcutta'
CACHE_TYPE = 'redis'
