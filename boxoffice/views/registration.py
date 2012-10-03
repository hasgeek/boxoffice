

from flask import render_template, g, session, redirect
import simplejson as json
from boxoffice import app
from boxoffice.views.login import lastuser

from boxoffice.models.order import Order

from boxoffice.forms.attendee import RegistrationForm

lastuser.external_resource('invoice/new', 'http://billing.hasgeek.in/api/newinvoice', 'POST')


@app.route('/orders/registration', methods=['GET', 'POST'])
@lastuser.requires_login
def registration():
    order = Order.query.get(session['order'])
    form = RegistrationForm()
    form = assign_attendees(order=order, form=form)
    data = json.dumps({
                'order': order.id,
                'title': app.config['TICKET_INVOICE_TITLE'],
                'lineitems': [line.as_json() for line in order.lineitems]},
                use_decimal=True, sort_keys=True, indent=4)
    message = None
    if form.validate_on_submit():
        foo = lastuser.call_resource(
            name='invoice/new',
            profileid=g.user.userid,
            workspace='hasgeek',
            data=data,
            headers={'Content-Type': 'application/json'})

        #check for url or error
        redirect_url = foo.get('url', None)
        if redirect_url:
            return redirect(redirect_url, code=303)
        else:
            message = foo.get('error', None)
    return render_template('registration.html', form=form, order=order, message=message)


def assign_attendees(order, form):
    append_flag = 1
    if get_attendees(order) == form.attendees.__len__():
        append_flag = 0

    x = 0
    for i, l in enumerate(order.lineitems):
        q = l.quantity
        c = l.category.title
        e = l.category.event.title
        for a in range(0, int(q)):
            if not (i == 0 and a == 0):
                if append_flag:
                    form.attendees.append_entry()
                form.attendees[x].name = e + ': Attendee #' + str(x + 1) + ' \n (' + c + ')'
                x = x + 1
            else:
                form.attendees[0].name = e + ': Attendee #1' + '\n (' + c + ')'
                x = x + 1
    return form


def get_attendees(order):
    x = 0
    for i, l in enumerate(order.lineitems):
        x = x + l.quantity
    return x
