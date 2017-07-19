from st2client.client import Client
from st2client.models import KeyValuePair

API_KEY = 'YjRlNmI5MDczNWMwOTEzMTg0NDIzZDQxN2QyOTJiZDZjMWUzNWVhM2IxYWRhMGUwZGM4ZmVlOTFiZjkxODY5Yw'
# API_URL = 'https://localhost/api/v1'
API_URL = 'http://127.0.0.1:9101/v1/'

client = Client(api_url=API_URL, api_key=API_KEY)

#try:
    # print(client.keys.get_by_name('vlan:42'))
print("QUERY")
keys = client.keys.query(prefix="vlan")

for k in keys:
    print "Key :" + str(k.name)
    print "Value: " + str(k.value)

response = client.keys.update(KeyValuePair(name='testkey25', value='testvalue25'))
print(response)
print(dir(client.keys.create))

# keys = client.keys.get_all()

# for k in keys:
#    print "Key :" + str(k.name)
#    print "Value: " + str(k.value)

#except Exception as e:
#    exit(1)
