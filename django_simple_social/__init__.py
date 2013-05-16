__author__ = 'mattesnider'

__version__ = (0, 1, 9)


def autodiscover():
    """
    Auto-discover INSTALLED_APPS backends.py modules that inherit from
    GenericSocialUserBackend and fail silently when not present.
    This forces an import on them to register any backend classes.
    """
    from copy import copy

    from django.conf import settings
    from django.contrib.admin.sites import site
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)

        # Attempt to import the app's email module.
        try:
            before_import_registry = copy(site._registry)
            import_module('%s.backends' % app)
        except Exception, exc:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            # (see #8245).
            site._registry = before_import_registry

            # backends exists but import failed, raise the exception.
            if module_has_submodule(mod, 'backends'):
                raise Exception(
                    'Failed to import {0}.backends with error: {1}.'.format(
                        app, exc))
