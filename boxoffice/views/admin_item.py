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
        filtered_items = Item.query.join(ItemCollection).filter(
            ItemCollection.organization == organization).filter(
            Item.title.ilike('%{query}%'.format(query=search))).options(db.load_only('id', 'title')).all()
        return api_success(result={'items': [{'id': str(item.id), 'title': "{ic_title}: {title}".format(ic_title=item.item_collection.title, title=item.title)}
            for item in filtered_items]}, doc="Filtered items", status_code=200)
    else:
        return api_error(message='Missing search query', status_code=400)
