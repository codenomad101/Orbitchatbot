import os
import ssl
import urllib3
import requests
from urllib3.util.ssl_ import create_urllib3_context

# Completely disable SSL verification globally
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create unverified SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Monkey patch requests to disable SSL verification
old_request = requests.Session.request
def new_request(self, *args, **kwargs):
    kwargs['verify'] = False
    return old_request(self, *args, **kwargs)
requests.Session.request = new_request

# Monkey patch urllib3
class NoSSLContext:
    def wrap_socket(self, *args, **kwargs):
        kwargs['cert_reqs'] = ssl.CERT_NONE
        return ssl.create_default_context().wrap_socket(*args, **kwargs)

urllib3.util.ssl_.create_urllib3_context = lambda *args, **kwargs: NoSSLContext()