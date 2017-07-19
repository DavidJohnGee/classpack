## Sensor Information

__Sensor__

This sensor offers a simple REST API to create, delete and fetch VLAN information. This 'VLAN' information is stored using the ST2 KV store. Keys are stored with a prefix of 'vlan:'. For example, you can create VLAN 42 and it would appear like this:

```
+---------+--------------------+--------+-----------+--------------+------+------------------+
| name    | value              | secret | encrypted | scope        | user | expire_timestamp |
+---------+--------------------+--------+-----------+--------------+------+------------------+
| vlan:42 | vlan of all things | False  | False     | st2kv.system |      |                  |
+---------+--------------------+--------+-----------+--------------+------+------------------+  
```

A Swagger server is available on the following URL so you can avoid using PostMan: http://<address>:12021/static/swagger-ui/index.html
Currently authentication isn't built in code. If you wanted to productionise this, security is a requirement.

__Security__

Nothing is built in. Again, NOTHING!

This sensor is a classroom experiment to demonstrate what is possible.

Security approaches could be:
- Use basic authentication and wire the sensor up through NGINX (for HTTPS offload)
- Use HTTPS and Oauth.

__Sensor Operations__

Three operations are available to you:
- GET
- POST
- DELETE

Each operation emits a trigger with three inputs:
- operation (string)
- vlan (string)
- description (string)

Depending on what operation and combination of values is passed in, the trigger contents will be different. Here is real world output.

{'operation': 'delete', 'vlan': '42', 'description': 'deleted'}
{'operation': 'delete', 'vlan': '42', 'description': '__cache_miss__'}
{'operation': 'get', 'vlan': '__get_all__', 'description': 'vlan_query'}
{'operation': 'set', 'vlan': '42', 'description': 'string'}
{'operation': 'set', 'vlan': '42', 'description': '__exists__'}
{'operation': 'get', 'vlan': '__get_all__', 'description': 'vlan_query'}
{'operation': 'delete', 'vlan': '42', 'description': 'deleted'}
{'operation': 'get', 'vlan': '__get_all__', 'description': 'vlan_query'}
{'operation': 'set', 'vlan': '42', 'description': 'string'}
{'operation': 'set', 'vlan': '42', 'description': '__exists__'}
