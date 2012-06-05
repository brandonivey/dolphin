
from django.contrib.auth.models import User
from django.contrib.gis.geos import fromstr
from fixture_generator import fixture_generator
from geoposition import Geoposition

from .models import FeatureFlag

@fixture_generator(FeatureFlag)
def test_base_flags():
    FeatureFlag.objects.create(id=1, name="enabled", enabled=True)
    FeatureFlag.objects.create(id=2, name="disabled", enabled=False)

@fixture_generator(User)
def test_users():
    User.objects.create(username="registered")
    User.objects.create(username="staff", is_staff=True)
    u = User(username='admin', is_staff=True, is_superuser=True)
    u.set_password('admin')
    u.save()

@fixture_generator(FeatureFlag, requires=["dolphin.test_base_flags", "dolphin.test_users"])
def test_user_flags():
    FeatureFlag.objects.create(id=3, name="registered_only", enabled=True, registered_only=True)
    FeatureFlag.objects.create(id=4, name="staff_only", enabled=True, staff_only=True)
    ff = FeatureFlag.objects.create(id=5, name="selected_users", enabled=True, limit_to_users=True)
    ff.users.add(User.objects.get(username="registered"))
    ff.save()

@fixture_generator(FeatureFlag, requires=['dolphin.test_base_flags'])
def test_regional_flags():
    FeatureFlag.objects.create(id=6, name='regional', enabled=True, enable_geo=True, center=Geoposition(37, -97), radius=100)
    FeatureFlag.objects.create(id=7, name='regional_5', enabled=True, enable_geo=True, center=Geoposition(37, -97), radius=5)


@fixture_generator(FeatureFlag, requires=['dolphin.test_base_flags'])
def test_ab_flags():
    FeatureFlag.objects.create(id=8, name='ab_random', enabled=True, random=True)
    FeatureFlag.objects.create(id=9, name='max', enabled=True, maximum_b_tests=5)
