"""
Copyright 2017 David Gee

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


# See ../requirements.txt

from __future__ import absolute_import
import eventlet
from st2reactor.sensor.base import Sensor
from st2client.client import Client
from st2client.models import KeyValuePair
from flask import request, Flask, Response, jsonify
from functools import wraps
import v1

eventlet.monkey_patch(
    os=True,
    select=True,
    socket=True,
    thread=True,
    time=True)

#<------------------------------------------------------->
# TODO(davidjohngee): Need to find a nicer way of passing in parameters for auth

_username = ""
_password = ""

#<------------------------------------------------------->
# Auth Helpers

def authenticate():
    """Send a 401 response that enables basic auth."""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def check_auth(username, password):
    """Check if a username and password combo is valid."""
    return username == _username and password == _password


def requires_auth(f):
    """Wrapper function."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


#<------------------------------------------------------->
class ClassSensor(Sensor):
    """This Sensor sets up the Class Sensor Service base information."""

    def __init__(self, sensor_service, config=None):
        """Stuff."""
        super(ClassSensor, self).__init__(sensor_service, config)

        # Setup our logger for debugging
        self._logger = self._sensor_service.get_logger(__name__)

        # Setup the basics
        self._sensor_listen_ip = '0.0.0.0'
        self._sensor_listen_port = config['sensorport']

        # Now set the global username and passwords for auth
        self._username = 'admin'
        self._password = config['username']
        self._password = config['password']
        global _username
        global _password
        _username = self._username
        _password = self._password

        self.receivedcall = 'classpack.receivedcall'

        # Register the Flask Swagger App
        self.app = Flask(__name__, static_folder='static')
        self.app.register_blueprint(
            v1.bp,
            url_prefix='/v1')

        # Create the ST2 client
        self.client = Client(base_url='http://localhost')

        # This triggers a bug. TODO(davidjohngee) Open bug case
        #
        # self.client = Client(api_url=self._apiurl, api_key=self._apikey)


    def setup(self):
        pass

    def run(self):

        # <------------------------------------------------------->
        # GET FUNCTION HANDLER FOR VLAN

        @self.app.route("/v1/vlan/<vlan_number>", methods=['GET'])
        def get(vlan_number):

            vlan = vlan_number

            # If not empty, then let's build the key index value
            if vlan !=  "{vlan_number}":
                vlan = "vlan:" + str(vlan_number)

            # Create a data structure to return
            # vlanlist = []

            if vlan == "{vlan_number}":
                queryresult = self.client.keys.query(prefix="vlan")
                vlanlist = []
                for thing in queryresult:
                    self._logger.info(type(thing))
                    if isinstance(thing, list):
                        keys = thing
                        for k in keys:
                            _name = k.name
                            _num = _name.split(':')[1]
                            _desc = k.value
                            _structure = {"number": _num, "description": _desc}
                            vlanlist.append(_structure)

                # Dispatch Trigger
                self._process_request("get", "__get_all__", "vlan_query" )

                # Return what we have
                return jsonify(vlanlist), 200, None

            else:
                k = self.client.keys.get_by_name(vlan)
                if k is None:
                    return jsonify([]), 200, None
                else:
                    vlanlist = []


                    _name = k.name
                    # Split the string to get just the number
                    _num = _name.split(':')[1]
                    _structure = {"number": _num, "description": k.value}

                    vlanlist.append(_structure)

                    # Dispatch Trigger
                    self._process_request("get", _num, k.value)

                    return jsonify(vlanlist), 200, None

        # <------------------------------------------------------->
        # POST FUNCTION HANDLER FOR VLAN

        @self.app.route("/v1/vlan/<vlan_number>", methods=['POST'])
        def post(vlan_number):

            if 'description' in request.json:
                description = request.json['description']
            else:
                description = "{description}"

            vlan = vlan_number
            # Get vlan input and check that for empty condition
            if vlan == "{vlan_number}":
                vlan = None

            # If not empty, then let's build the key index value
            if vlan is not None:
                vlan = "vlan:" + str(vlan_number)


            # See if the key exists
            k = self.client.keys.get_by_name(vlan)

            if k is not None:
                _return = {"number": vlan_number, "description": "__exists__"}

                # Dispatch Trigger
                self._process_request("set", str(vlan_number), "__exists__")

                # return jsonify(_return), 201, None
            else:
                if vlan is not None:
                    self.client.keys.update(KeyValuePair(name=str(vlan), value=str(description)))

                    # Dispatch Trigger
                    self._process_request("set", str(vlan_number), str(description))

                    _return = {"number": vlan_number, "description": description}
                else:
                    _return = None


            return jsonify(_return), 201, None

        # <------------------------------------------------------->
        # DELETE FUNCTION HANDLER FOR VLAN

        @self.app.route("/v1/vlan/<vlan_number>", methods=['DELETE'])
        def delete(vlan_number):

            vlan = vlan_number
            # Get vlan input and check that for empty condition
            if vlan == "{vlan_number}":
                vlan = None

            # If not empty, then let's build the key index value
            if vlan is not None:
                vlan = "vlan:" + str(vlan_number)

            # Query it to see if it needs deleting
            k = self.client.keys.get_by_name(vlan)

            if k is not None:
                # Key exists, delete it
                self.client.keys.delete(KeyValuePair(name=str(vlan)))
                _return = {"number": vlan_number, "description": "deleted"}

                # Dispatch Trigger
                self._process_request("delete", str(vlan_number), "deleted")
                # return jsonify(_return), 201, None
            else:
                # Nothing to delete
                _return = {"number": vlan_number, "description": "__cache_miss__"}

                # Dispatch Trigger
                self._process_request("delete", str(vlan_number), "__cache_miss__")



            return jsonify(_return), 201, None

        #<------------------------------------------------------->

        self.app.run(debug=True,
                host=self._sensor_listen_ip,
                port=int(self._sensor_listen_port))


    # You might be tempted to delete the unused methods. Don't! It will fail validation for the runner.

    def cleanup(self):
        """Stuff."""
        pass

    def add_trigger(self, trigger):
        """Stuff."""
        pass

    def update_trigger(self, trigger):
        """Stuff."""
        pass

    def remove_trigger(self, trigger):
        """Stuff."""
        pass

    # <------------------------------------------------------->

    def _process_request(self, operation, vlan, description):
        # Simple method that dispatches a Trigger
        payload = {"operation": operation, "vlan": vlan, "description": description}
        self._sensor_service.dispatch(trigger=self.receivedcall, payload=payload)
        return
