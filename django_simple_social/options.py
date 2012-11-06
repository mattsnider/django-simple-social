from django.conf import settings

# The namespace your application registered django_social_user under.
#   The recommended setting is ``django_social_user``.
DJANGO_SOCIAL_USER_NAMESPACE = getattr(settings,
    'DJANGO_SOCIAL_USER_NAMESPACE', 'django_social_user')
