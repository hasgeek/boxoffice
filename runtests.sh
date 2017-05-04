#!/bin/sh
export FLASK_ENV="TESTING"
coverage run `nosetests -v tests`
