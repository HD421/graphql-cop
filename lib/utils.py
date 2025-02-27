"""Helper parts for graphql-cop."""
import requests
from simplejson import JSONDecodeError
from version import VERSION

requests.packages.urllib3.disable_warnings()

def curlify(obj):
  req = obj.request
  command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
  method = req.method
  uri = req.url
  if req.body:
    data = req.body.decode('UTF-8')
  else:
    data = ''
  headers = ['"{0}: {1}"'.format(k, v) for k, v in req.headers.items()]
  headers = " -H ".join(headers)
  return command.format(method=method, headers=headers, data=data, uri=uri)

def get_error(resp):
  """Collect the error."""
  error = None
  try:
      error = resp['errors'][0]['message']
  except:
      pass
  return error

def graph_query(url, proxies, headers, operation='query', payload={}, batch=False):
  """Perform a query."""
  
  if batch:
    data = []
    for _ in range(10):
      data.append({operation:payload})
  else:
    data = {operation:payload}
  
  try:
    response = requests.post(url,
                            headers=headers,
                            cookies=None,
                            verify=False,
                            allow_redirects=True,
                            timeout=60,
                            proxies=proxies,
                            json=data)
    return response
  except Exception:
    return {}


def request_get(url, proxies, headers, params=None, data=None):
  """Perform requests."""
  try:
    response = requests.get(url,
                            params=params,
                            headers=headers,
                            cookies=None,
                            verify=False,
                            allow_redirects=True,
                            proxies=proxies,
                            timeout=5, 
                            data=data)
    return response
  except:
    return None

def is_graphql(url, proxies, headers):
  """Check if the URL provides a GraphQL interface."""
  query = '''
    query {
      __typename
    }
  '''
  response = graph_query(url, proxies, headers, payload=query)

  try:
    response.json()
  except AttributeError:
    return False
  except JSONDecodeError:
    return False

  if response.json().get('data', {}).get('__typename', '') in ('Query', 'QueryRoot', 'query_root'):
    return True
  elif response.json().get('errors') and (any('locations' in i for i in response['errors']) or (any('extensions' in i for i in response))):
    return True
  elif response.json().get('data'):
    return True
  else:
    return False

def draw_art():
  """Create banner."""
  return '''
                GraphQL Cop {version}
           Security Auditor for GraphQL
             Dolev Farhi & Nick Aleks
  '''.format(version=VERSION)
