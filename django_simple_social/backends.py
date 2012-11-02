from urllib import urlencode
from django.conf import settings

from django.core.validators import email_re
from django_social_user import register_backend
from django_social_user.backends import GenericSocialUserBackend
from django_social_user.exceptions import SocialOauthDictFailed

from linkedin_json_client.api import LinkedInJsonAPI
from linkedin_json_client.constants import (
    BasicProfileFields, LinkedInScope, BasicProfileSelectors)

LINKED_IN_SELECTORS = [
    BasicProfileSelectors.ID,
    BasicProfileSelectors.FIRST_NAME,
    BasicProfileSelectors.LAST_NAME,
    BasicProfileSelectors.LOCATION,
    BasicProfileSelectors.PUBLIC_PROFILE_URL,
    BasicProfileSelectors.PICTURE_URL,
    BasicProfileSelectors.MAIN_ADDRESS
]

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
                client = LinkedInJsonAPI(linkedin_ck, linkedin_cs)
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
        return '%s@proxymail.linkedin.com' % oauth_obj.get(
            BasicProfileFields.ID)

    def get_first_name(self, oauth_obj):
        return oauth_obj.get(BasicProfileFields.FIRST_NAME) or ''

    def get_last_name(self, oauth_obj):
        return oauth_obj.get(BasicProfileFields.LAST_NAME) or ''

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

    def get_oauth_authorization_url(self, oauth_request_token):
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
                BasicProfileFields.ID))
        else:
            raise SocialOauthDictFailed

    def get_oauth_request_token(self):
        return self.client.get_request_token(scope=[
            LinkedInScope.BASIC_PROFILE, LinkedInScope.EMAIL_ADDRESS,
            LinkedInScope.NETWORK_UPDATES, LinkedInScope.CONNECTIONS,
            LinkedInScope.CONTACT_INFO, LinkedInScope.MESSAGES])

    def get_username(self, oauth_obj):
        return '%s %s' % (
            self.get_first_name(oauth_obj), self.get_last_name(oauth_obj))
register_backend(LinkedInBackend)
