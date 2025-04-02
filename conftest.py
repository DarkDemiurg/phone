"""Pytest setup"""


def pytest_configure(config):
    # NB this causes `phone_app/__init__.py` to run
    import phone_app  # noqa
