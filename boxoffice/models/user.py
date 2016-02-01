# -*- coding: utf-8 -*-
from flask import g
from flask.ext.lastuser.sqlalchemy import UserBase2, ProfileBase
from boxoffice.models import db


__all__ = ['User', 'Organization']


class User(UserBase2, db.Model):

    __tablename__ = 'user'

    def __repr__(self):
        return self.fullname


def default_user(context):
    return g.user.id if g.user else None


class Organization(ProfileBase, db.Model):
    __tablename__ = 'organization'
