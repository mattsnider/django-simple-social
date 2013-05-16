from datetime import datetime, timedelta
from urllib import urlencode

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import email_re
from django_social_user.backends import GenericSocialUserBackend
from django_social_user.exceptions import SocialOauthDictFailed

# social network APIs
import facebook
from linkedin_json_client import api as li_api, constants as li_constants
from twython import Twython

from django_simple_social import options

LINKED_IN_SELECTORS = [
    li_constants.BasicProfileSelectors.ID,
    li_constants.BasicProfileSelectors.FIRST_NAME,
    li_constants.BasicProfileSelectors.LAST_NAME,
    li_constants.BasicProfileSelectors.LOCATION,
    li_constants.BasicProfileSelectors.PUBLIC_PROFILE_URL,
    li_constants.BasicProfileSelectors.PICTURE_URL,
    li_constants.BasicProfileSelectors.MAIN_ADDRESS
]


class FacebookBackend(GenericSocialUserBackend):
    """
    Backend for working with Facebook
    """
    network = 'facebook'

    def __init__(self):
        super(FacebookBackend, self).__init__()
        self.facebook_ck = getattr(settings, 'FACEBOOK_CONSUMER_KEY', '')
        self.facebook_cs = getattr(settings, 'FACEBOOK_CONSUMER_SECRET', '')

    def get_callback_url(self, url_prefix):
        """
        Generate the callback URL for Facebook to pass ``code`` to.
        """
        return '%s%s' % (url_prefix, reverse(
            '%s:callback' % getattr(options, 'DJANGO_SOCIAL_USER_NAMESPACE'),
            args=[self.network]))

    def get_email(self, oauth_obj):
        """
        won't ever get email here, so just return empty string
        """
        return ''

    def get_first_name(self, oauth_obj):
        return oauth_obj['first_name']

    def get_last_name(self, oauth_obj):
        return oauth_obj['last_name']

    def get_oauth_access_token(self, request, oauth_request_token):
        """
        Get the access token using the oauth request token and the data
        provided on the request. Should raise the appropriate exception
        if the data is invalid. Returns an object like:
        {
            'oauth_token_secret': 'ASDF',
            'user_id': '1234',
            'oauth_token': '123-asdf',
            'screen_name': 'mattsniderjs'
        }
        """
        code = request.GET.get('code')

        if not code:
            raise SocialOauthDictFailed

        url_prefix = 'https' if request.is_secure() else 'http'
        url_prefix += '://%s' % request.META['HTTP_HOST']

        data = facebook.get_access_token_from_code(
            code, self.get_callback_url(url_prefix), self.facebook_ck,
            self.facebook_cs)

        if not (data.get('access_token') and data.get('expires')):
            raise SocialOauthDictFailed

        return data['access_token'], datetime.now() + timedelta(
            milliseconds=int(data['expires']))

    def get_oauth_authorization_url(
            self, oauth_request_token, url_prefix='', params=None):
        if params and 'scope' in params:
            perms = params['scope'].split(',')
        else:
            perms = {}
        return facebook.auth_url(
            self.facebook_ck, self.get_callback_url(url_prefix), perms=perms)

    def get_oauth_dict(self, access_token):
        """
        Uses the access token to find the LinkedIn user object,
        then returns it and the account uid.
        """
        if not access_token:
            raise SocialOauthDictFailed

        graph = facebook.GraphAPI(access_token)

        oauth_object = graph.get_object('me')

        if oauth_object:
            return oauth_object, unicode(oauth_object['id'])
        else:
            raise SocialOauthDictFailed

    def get_oauth_request_token(self):
        return 1

    def get_username(self, oauth_obj):
        # If the Facebook account data does not contain a username (Facebook
        # test users can't have usernames) use the id instead.
        if 'username' in oauth_obj:
            return oauth_obj['username']
        else:
            return oauth_obj['id']


class LinkedInBackend(GenericSocialUserBackend):
    """
    Backend for working with LinkedIn
    """
    network = 'linkedin'

    @property
    def client(self):
        client = getattr(self, '_client', None)

        if not client:
            linkedin_ck = getattr(settings, 'LINKED_IN_CONSUMER_KEY', '')
            linkedin_cs = getattr(settings, 'LINKED_IN_CONSUMER_SECRET', '')

            # if LinkedIn is configured, create the client
            if linkedin_ck and linkedin_cs:
                client = li_api.LinkedInJsonAPI(linkedin_ck, linkedin_cs)
            else:
                raise NotImplementedError()
            self._client = client
        return client

    def get_email(self, oauth_obj):
        emails = oauth_obj.get('email') or ''
        if '@' in emails:
            for line in emails.split('\n'):
                line = line.strip()
                if email_re.match(line):
                    return line
        return ''

    def get_first_name(self, oauth_obj):
        return oauth_obj.get(li_constants.BasicProfileFields.FIRST_NAME) or ''

    def get_last_name(self, oauth_obj):
        return oauth_obj.get(li_constants.BasicProfileFields.LAST_NAME) or ''

    def get_oauth_access_token(self, request, oauth_request_token):
        """
        Get the access token using the oauth request token and the data
        provided on the request. Should raise the appropriate exception
        if the data is invalid.
        """
        oauth_verifier = request.GET.get('oauth_verifier')
        oauth_problem = request.GET.get('oauth_problem')
        if oauth_problem or oauth_request_token is None:
            raise SocialOauthDictFailed

        return self.client.get_access_token(
            oauth_request_token, oauth_verifier), None

    def get_oauth_authorization_url(
            self, oauth_request_token, url_prefix='', params=None):
        return u'%s?%s' % (
            self.client.authorize_path, urlencode(oauth_request_token))

    def get_oauth_dict(self, access_token):
        """
        Uses the access token to find the LinkedIn user object,
        then returns it and the account uid.
        """
        if not access_token or 'token_rejected' in access_token:
            raise SocialOauthDictFailed

        oauth_object = self.client.get_user_profile(
            access_token, selectors=LINKED_IN_SELECTORS)

        if oauth_object:
            oauth_object['email'] = self.client.get_email_address(
                access_token)
            return oauth_object, unicode(oauth_object.get(
                li_constants.BasicProfileFields.ID))
        else:
            raise SocialOauthDictFailed

    def get_oauth_request_token(self):
        return self.client.get_request_token(scope=[
            li_constants.LinkedInScope.BASIC_PROFILE,
            li_constants.LinkedInScope.EMAIL_ADDRESS,
            li_constants.LinkedInScope.NETWORK_UPDATES,
            li_constants.LinkedInScope.CONNECTIONS,
            li_constants.LinkedInScope.CONTACT_INFO,
            li_constants.LinkedInScope.MESSAGES])

    def get_username(self, oauth_obj):
        return '%s %s' % (
            self.get_first_name(oauth_obj), self.get_last_name(oauth_obj))


class TwitterBackend(GenericSocialUserBackend):
    """
    Backend for working with Twitter
    """
    network = 'twitter'

    def __init__(self):
        super(TwitterBackend, self).__init__()
        self.twitter_ck = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
        self.twitter_cs = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')

    @property
    def client(self):
        client = getattr(self, '_client', None)

        if not client:
            # if LinkedIn is configured, create the client
            if self.twitter_ck and self.twitter_cs:
                client = Twython(
                    app_key=self.twitter_ck, app_secret=self.twitter_cs)
            else:
                raise NotImplementedError()
            self._client = client
        return client

    def get_email(self, oauth_obj):
        emails = oauth_obj.get('email') or ''
        if '@' in emails:
            for line in emails.split('\n'):
                line = line.strip()
                if email_re.match(line):
                    return line
        return ''

    def get_first_name(self, oauth_obj):
        name_tokens = oauth_obj['name'].split(' ')
        return name_tokens[0]

    def get_last_name(self, oauth_obj):
        name_tokens = oauth_obj['name'].split(' ')
        return ' '.join(name_tokens[1:])

    def get_oauth_access_token(self, request, oauth_request_token):
        """
        Get the access token using the oauth request token and the data
        provided on the request. Should raise the appropriate exception
        if the data is invalid. Returns an object like:
        {
            'oauth_token_secret': 'ASDF',
            'user_id': '1234',
            'oauth_token': '123-asdf',
            'screen_name': 'mattsniderjs'
        }
        """
        oauth_verifier = request.GET.get('oauth_verifier')
        oauth_token = request.GET.get('oauth_token')

        if not (oauth_verifier and oauth_token) or (
            oauth_token != oauth_request_token['oauth_token']):
            raise SocialOauthDictFailed

        client = Twython(
            app_key=self.twitter_ck, app_secret=self.twitter_cs,
            **self.parse_oauth_token(oauth_request_token))

        return client.get_authorized_tokens(), None

    def get_oauth_authorization_url(
            self, oauth_request_token, url_prefix='', params=None):
        return oauth_request_token['auth_url']

    def get_oauth_dict(self, access_token):
        """
        Uses the access token to find the LinkedIn user object,
        then returns it and the account uid.
        """
        if not access_token or 'token_rejected' in access_token:
            raise SocialOauthDictFailed

        client = Twython(
            app_key=self.twitter_ck, app_secret=self.twitter_cs,
            **self.parse_oauth_token(access_token))

        oauth_object = client.get('users/show', params={
            'user_id': access_token['user_id']
        })

        if oauth_object:
            return oauth_object, unicode(access_token['user_id'])
        else:
            raise SocialOauthDictFailed

    def get_oauth_request_token(self):
        return self.client.get_authentication_tokens()

    def get_username(self, oauth_obj):
        return oauth_obj['screen_name']

    def parse_oauth_token(self, access_token):
        """
        Expects an object like the following as the access token,
        and returns a dictionary of oauth_token and oauth_token_secret
        for use with Twython constructor.
        {
            'oauth_token_secret': 'ASDF',
            'user_id': '1234',
            'oauth_token': '123-asdf',
            'screen_name': 'mattsniderjs'
        }
        """
        return {
            'oauth_token': access_token['oauth_token'],
            'oauth_token_secret': access_token['oauth_token_secret'],
            }
