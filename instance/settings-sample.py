#: Google Analytics tracking code
GA_CODE = 'UA-XXXXXXX-X'
#: Typekit font code, from the embed URL: http://use.typekit.com/(code).js
TYPEKIT_CODE = ''
#: Database backend
SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
#: Secret key
SECRET_KEY = 'make this something random'  # nosec
#: Timezone for displayed datetimes
TIMEZONE = 'Asia/Kolkata'
#: Mail settings
#: MAIL_FAIL_SILENTLY : default True
#: MAIL_SERVER : default 'localhost'
#: MAIL_PORT : default 25
#: MAIL_USE_TLS : default False
#: MAIL_USE_SSL : default False
#: MAIL_USERNAME : default None
#: MAIL_PASSWORD : default None
#: DEFAULT_MAIL_SENDER : default None
MAIL_FAIL_SILENTLY = False
MAIL_SERVER = 'localhost'
DEFAULT_MAIL_SENDER = ('DocType HTML5', 'test@example.com')
#: Show Google Ads
GOOGLE_AD_CLIENT = ''
GOOGLE_AD_SLOT = ''
GOOGLE_AD_WIDTH = 0
GOOGLE_AD_HEIGHT = 0
#: Lastuser server
LASTUSER_SERVER = 'https://hasgeek.com/'
#: Lastuser client id
LASTUSER_CLIENT_ID = ''
#: Lastuser client secret
LASTUSER_CLIENT_SECRET = ''  # nosec
#: Cache settings
CACHE_TYPE = 'redis'
#: RQ settings
RQ_REDIS_URL = 'redis://localhost:6379/0'
RQ_SCHEDULER_INTERVAL = 1

#: Allowed origins
ALLOWED_ORIGINS = [
    'http://boxoffice.test:6500',  # Own host must always be present
    'http://funnel.test',
    'http://funnel.test:3000',
]
