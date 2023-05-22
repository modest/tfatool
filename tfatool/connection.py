import requests
import logging
from enum import Enum
from .info import AuthMode


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Connection:
  def __init__(self, url: str, user=None, password=None, auth_name=None):
    self._url = url
    self.user = user
    self.password = password
    
    # connection properties
    if auth_name and auth_name != 'none':
        self._auth = AuthMode[auth_name]
    elif user or password:
        self._auth = AuthMode.basic
    else:
        self._auth = AuthMode.none
  
  @property
  def auth_object(self):
    if self.auth == AuthMode.basic:
        return requests.auth.HTTPBasicAuth(self.user, self.password)
    elif self.auth == AuthMode.digest:
        return requests.auth.HTTPDigestAuth(connection.user, connection.password)
    else:
        return None
      
  @property  
  def auth_name(self):
    return self.auth.name
    
  @property
  def auth(self):
    return self._auth
    
  @property
  def url(self):
    return self._url
    

DEFAULT_CONNECTION = Connection(url="http://flashair/", user=None, password=None, auth_name="none")
