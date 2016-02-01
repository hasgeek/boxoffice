# -*- coding: utf-8 -*-
from flask import g
from flask.ext.lastuser.sqlalchemy import UserBase2, ProfileBase
from boxoffice.models import db, IdMixin


__all__ = ['User', 'Organization', 'Customer']


class User(UserBase2, db.Model):

    __tablename__ = 'user'

    def __repr__(self):
        return self.fullname


def default_user(context):
    return g.user.id if g.user else None


class Organization(ProfileBase, db.Model):
    __tablename__ = 'organization'


class Customer(IdMixin, db.Model):
    __tablename__ = 'customer'
    __uuid_primary_key__ = True

    fullname = db.Column(db.Unicode(80), nullable=False)
    #: Unvalidated email address
    email = db.Column(db.Unicode(254), nullable=False)
    #: Unvalidated phone number
    phone = db.Column(db.Unicode(80), nullable=True)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    address = db.Column(db.Unicode(256), nullable=False)

    account_id = db.Column(None, db.ForeignKey('customer.id'))
    account = db.relationship("Account", back_populates="customer")
