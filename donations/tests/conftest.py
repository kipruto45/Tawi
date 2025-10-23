import django
from django.template.engine import Engine


def pytest_configure(config):
    """When pytest is used, ensure the test filter is available as a builtin.

    Note: This is a pytest hook, and will only run if tests are executed with pytest.
    We also add the builtin to Django's default Engine for manage.py test runs below.
    """
    try:
        Engine.get_default().builtins.append('core.templatetags.test_filters')
    except Exception:
        pass
