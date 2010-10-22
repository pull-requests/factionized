try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

context = local()
