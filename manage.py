#!/usr/bin/env python
import os
import sys

# Monkey-patch djongo to avoid truth-testing the Database object on close
try:
    import djongo.base
    djongo.base.Database._close = lambda self: None
except ImportError:
    pass

# Monkey-patch pymongo Database __bool__ to prevent NotImplementedError
try:
    import pymongo.database
    pymongo.database.Database.__bool__ = lambda self: False
except ImportError:
    pass


def main():
    """
    Run administrative tasks.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banana_supply_chain.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
