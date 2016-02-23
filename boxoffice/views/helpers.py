from boxoffice import lastuser
from boxoffice.models import User


def find_or_create_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    return lastuser.usermanager.create_user(email=email)
