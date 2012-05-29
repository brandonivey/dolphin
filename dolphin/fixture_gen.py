from fixture_generator import fixture_generator

from django.contrib.auth.models import User

from .models import FeatureFlag

@fixture_generator(FeatureFlag)
def test_base_flags():
    FeatureFlag.objects.create(name="enabled", enabled=True)
    FeatureFlag.objects.create(name="disabled", enabled=False)

@fixture_generator(User)
def test_users():
    User.objects.create(username="registered")
    User.objects.create(username="staff", is_staff=True)

@fixture_generator(FeatureFlag, requires=["dolphin.test_base_flags", "dolphin.test_users"])
def test_user_flags():
    FeatureFlag.objects.create(name="registered_only", enabled=True, registered_only=True)
    FeatureFlag.objects.create(name="staff_only", enabled=True, staff_only=True)
    ff = FeatureFlag.objects.create(name="selected_users", enabled=True, limit_to_users=True)
    ff.users.add(User.objects.get(username="registered"))
    ff.save()
