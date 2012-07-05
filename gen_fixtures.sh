#!/bin/bash

python manage.py generate_fixture dolphin.test_base_flags > dolphin/fixtures/dolphin_base_flags.json
python manage.py generate_fixture dolphin.test_users > dolphin/fixtures/dolphin_users.json
python manage.py generate_fixture dolphin.test_user_flags > dolphin/fixtures/dolphin_user_flags.json
python manage.py generate_fixture dolphin.test_regional_flags > dolphin/fixtures/dolphin_regional_flags.json
python manage.py generate_fixture dolphin.test_ab_flags > dolphin/fixtures/dolphin_ab_flags.json
