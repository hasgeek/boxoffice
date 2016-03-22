#!/usr/bin/env python
# -*- coding: utf-8 -*-
from boxoffice import init_for, app

if __name__ == '__main__':
    init_for('dev')
    # To insert seed data, please run relevant file under scripts/
app.run('0.0.0.0', port=6500, threaded=True)
