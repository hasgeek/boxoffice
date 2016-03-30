#: App settings
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI='postgresql://@localhost:5432/boxoffice'
ALLOWED_ORIGINS=['http://localhost:6600']
TIMEZONE = 'Asia/Calcutta'
SECRET_KEY='make this something random'

#: LastUser server
LASTUSER_SERVER='http://auth.hasgeek.com'
LASTUSER_CLIENT_ID=''
LASTUSER_CLIENT_SECRET=''

#: Razorpay payment gateway
RAZORPAY_KEY_ID=''
RAZORPAY_KEY_SECRET=''

#: Data settings
ITEM_COLLECTION_ID=''

#: Scripts settings
WEBHOOK_URL=''
