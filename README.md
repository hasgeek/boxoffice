### Boxoffice: Hasgeek's ticketing system
[![Build Status](https://travis-ci.org/hasgeek/boxoffice.svg?branch=v0.2)](https://travis-ci.org/hasgeek/boxoffice)

## Asset builds

Run

```
make
```

## Deployment

```
createdb boxoffice
pip install -r requirements.txt
flask dbconfig | sudo -c postgres psql boxoffice
# Config in instance/settings.py
# Development server: ./runserver.py
# Production: point a WSGI gateway at website.py
```

Copyright © 2015-2020 by [Hasgeek Learning Private Limited](https://hasgeek.com/about)
