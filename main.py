import requests
import json

OAUTH_URL = 'https://allegro.pl/auth/oauth'
REDIRECT_URI = 'http://localhost:8000'


def get_OAuth_token(client_id, client_secret, oauth_url=OAUTH_URL, redirect_uri=REDIRECT_URI):
    url = f'{oauth_url}/authorize?response_type=code&client_id={client_id}' \
          f'&client_secret={client_secret}&redirect_uri={redirect_uri}'
    parsed_redirect_uri = requests.utils.urlparse(redirect_uri)
    server_address = parsed_redirect_uri.hostname, parsed_redirect_uri.port