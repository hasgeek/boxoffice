# -*- coding: utf-8 -*-

from .. import app, lastuser
from coaster.views import load_models, requestargs
from boxoffice.models import db, Organization, ItemCollection, Item
from boxoffice.views.utils import api_error, api_success
from utils import xhr_only


@app.route('/admin/o/<org>/items')
@lastuser.requires_login
@xhr_only
@load_models(
    (Organization, {'name': 'org'}, 'organization'),
    permission='org_admin'
    )
@requestargs('search')
def items(organization, search=None):
    if search:
        filtered_items = db.session.query(Item, ItemCollection).filter(
            ItemCollection.organization == organization).filter(
            Item.title.ilike('%{query}%'.format(query=search))).join(Item.item_collection).options(
            db.Load(Item).load_only('id', 'title'),
            db.Load(ItemCollection).load_only('id', 'title')).all()
        return api_success(result={'items': [{
            'id': str(item_tuple[0].id),
            'title': "{ic_title}: {title}".format(ic_title=item_tuple[1].title, title=item_tuple[0].title)
        } for item_tuple in filtered_items]}, doc="Filtered items", status_code=200)
    else:
        return api_error(message='Missing search query', status_code=400)
