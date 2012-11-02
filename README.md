Introduction
============

The Django-Simple-Social library downloads a collection of social network libraries and
provides automatic backends, and interfaces for working with them. The goal of this project is to simplify working with third-party apps and authorization tools, such as Facebook, LinkedIn, and Twitter.

Make sure you also read up on Djagno-Social-User, as it provides the foundational infrastructure for this library:

    https://github.com/mattsnider/Djagno-Social-User

Keep in mind this library is still under development, so there may be breaking changes. I'll update the documentation anytime that happens, but feel free to contact me as well.

All functions and classes are documented inline. If you have additional questions, I can be reached on github or at admin@mattsnider.com.

Getting started
===============

Standard stuff applies to install. Use PIP to install with dependencies:

    pip install django-simple-social

Or install from the command line:

    python setup.py install

Dependencies
============

There many dependencies for this library, because it requires APIs for working with each social network:

    django 1.3 or greater
    Django-Social-User
    LinkedIn-API-JSON-Client

Usage Guide
===========

Register any social network backends you want to use in your settings.py:

    AUTHENTICATION_BACKENDS = (
        'django_simple_social.backends.LinkedInBackend',
        'django_simple_social.backends.TwitterBackend',
        ...
        'django.contrib.auth.backends.ModelBackend')

Add any required API keys (backend dependent) to settings.py, here are some examples:

    LINKED_IN_CONSUMER_KEY = 'wvso771yz9n7'
    LINKED_IN_CONSUMER_SECRET = 'QTOZ8W1jP9TSLqqF'

Run the backend autodiscover in urls.py:

    import django_simple_social; django_simple_social.autodiscover()

Include references to Django-Social-User urls in urls.py:

    urlpatterns = patterns('',
        ...
        url(r'^social/', include('django_social_user.urls', namespace='django_social_user')),
        ...
        (r'^admin/', include(admin.site.urls)),)

To begin the oauth process with a social network, expose the following link to an enduser:

    <a href="{% url 'django_social_user:authorize' 'facebook' %}">Sign in with Facebook</a>
    <a href="{% url 'django_social_user:authorize' 'linkedin' %}">Sign in with LinkedIn</a>
    <a href="{% url 'django_social_user:authorize' 'twitter' %}">Sign in with Twitter</a>

Todo
====

1. Support facebook
2. Support google
3. Support openid
4. Support twitter
5. Better error handling
6. Asynchronous/JS driven authentication, instead of browser redirects
7. Decouple APIs from this infrastructure and allow API customization