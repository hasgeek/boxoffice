# -*- coding: utf-8 -*-
from flask import g
from flask.ext.lastuser.sqlalchemy import UserBase2, ProfileBase
from boxoffice.models import db, JsonDict


__all__ = ['User', 'Organization']


class User(UserBase2, db.Model):

    __tablename__ = 'user'

    def __repr__(self):
        return self.fullname

    @property
    def orgs(self):
        return Organization.query.filter(Organization.userid.in_(self.organizations_owned_ids())).all()


def default_user(context):
    return g.user.id if g.user else None


class Organization(ProfileBase, db.Model):
    __tablename__ = 'organization'
    __table_args__ = (db.UniqueConstraint('contact_email'),)

    details = db.Column(JsonDict, nullable=False, server_default='{}')
    contact_email = db.Column(db.Unicode(254), nullable=False)

    def permissions(self, user, inherited=None):
        print "perms"
        perms = super(Organization, self).permissions(user, inherited)
        if self.userid in user.organizations_owned_ids():
            perms.update(['org_view'])
        return perms
