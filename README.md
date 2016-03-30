BoxOffice
=========

[![Build Status](https://travis-ci.org/hasgeek/boxoffice.svg?branch=order_ui)](https://travis-ci.org/hasgeek/boxoffice)

Boxoffice is HasGeek's ticketing system. It is the server that listens to calls by a client side widget and responds accordingly.

Usage for development
---------------------

__Part 1: Sever setup__

Clone the repository:

    $ git clone git@github.com:hasgeek/boxoffice.git
    $ cd boxoffice

We use Postgres for development so DB creation commands here are Postgres specific. Create the app db with:

    $ createdb boxoffice

Create `development.py` with:

    $ cp instance/settings-sample.py instance/development.py

If you have registered your client as app against our hosted Lastuser ([auth.hasgeek.com](http://auth.hasgeek.com)) then edit to add values for `LASTUSER_CLIENT_ID` and `LASTUSER_CLIENT_SECRET`.

Bring the created database up to date by running:

    $ python manage.py migrate dev upgrade head

Add dummy data with:

    $ python dummy_client/add_dummy_data.py

Extract the `itemCollection` `id` with this query:

    $ psql -d boxoffice -c "select id from item_collection";

Note down this value of `id` as we will later plug it into our dummy client. Also note that this `id` would change if you dropped the boxoffice DB and created again.

__Part 2: Client setup__

Edit the following variables in your `dummy_test_client.html`:

 * `boxofficeUrl="http://localhost:6500"`
 * Add the `itemCollection id` value you had noted down earlier to `itemCollection=""`

__Run the server__

Serve the dummy client with:

    $ cd dummy_client
    $ python -m SimpleHTTPServer 6600

Run the Boxoffice server with:

    $ python runserver.py

Now, you should be able access the Boxoffice widget on your dummy client at `http://localhost:6600`.

Tests
-----

The test setup is same as development set up but with testing environment variables.

Create `secrets.test` and set the variables in your environment with:

    $ cp secrets.test secrets.test.sample

Edit `secrets.test` to add keys as needed and set them as environment variables with:

    $ source secrets.test

To run tests, from root directory of the project:

    $ nosetests # Runs unit tests
    $ casperjs test tests # Runs integration tests

Optionally you can include the `--with-timer` flag with the `nosetests` command to see if there are tests that take longer than 1 second each.

Support
-------

Feel free to file a bug report for anything that doesn't work or is amiss in our code. When in doubt, leave us a message in #tech on [friendsofhasgeek.slack.com](http://friendsofhasgeek.slack.com).
