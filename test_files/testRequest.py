
import requests

response = requests.request("GET", "http://localhost:50011/api/machine/1/status/10", headers={'key': 'api_key'}, data={})

print(response.text)
