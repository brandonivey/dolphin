#!/bin/bash

python manage.py generate_fixture dolphin.test_base_flags > dolphin/fixtures/base_flags.json
python manage.py generate_fixture dolphin.test_users > dolphin/fixtures/users.json
python manage.py generate_fixture dolphin.test_user_flags > dolphin/fixtures/user_flags.json
