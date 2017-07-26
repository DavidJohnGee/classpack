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
import json

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

# <------------------------------------------------------->


class ClassSensor2(Sensor):
    """This Sensor sets up the Class Sensor Service base information."""

    def __init__(self, sensor_service, config=None):
        """Stuff."""
        super(ClassSensor2, self).__init__(sensor_service, config)

        # Setup our logger for debugging
        self._logger = self._sensor_service.get_logger(__name__)

        # Setup the basics
        self._sensor_listen_ip = '0.0.0.0'
        self._sensor_listen_port = config['sensor2port']

        # Now set the global username and passwords for auth
        self._username = 'admin'
        self._password = config['username']
        self._password = config['password']
        global _username
        global _password
        _username = self._username
        _password = self._password

        self.receivedcomplexcall = 'classpack.receivedcomplexcall'

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

    # <--------------- KV Store Helpers ------->

    def getkvdata(self, device=None, port=None):
        """
        Get data from the KV store.

        If device is None, then return all data.
        If device is not none, but port is none, return device data.
        """
        # Build the KV store query string
        if device is None and port is None:
            queryresult = self.client.keys.query(prefix="device:")
            # self._logger.info("QUERY RESULT: " + str(queryresult))
            devicelist = []
            for thing in queryresult:
                if isinstance(thing, list):
                    keys = thing
                    for k in keys:
                        _dev_temp = k.name
                        dev = _dev_temp.split(':')[1]
                        port = _dev_temp.split(':')[2]
                        attributes = json.loads(k.value)

                        _structure = {"device": dev, "port_id": port,
                                      "attributes": attributes}

                        devicelist.append(_structure)

            return devicelist

        if device is not None and port is None:
            querystring = "device:" + str(device)
            queryresult = self.client.keys.query(prefix=querystring)
            portlist = []
            for thing in queryresult:
                if isinstance(thing, list):
                    keys = thing
                    for k in keys:
                        _dev_temp = k.name
                        dev = _dev_temp.split(':')[1]
                        port = _dev_temp.split(':')[2]
                        attributes = json.loads(k.value)

                        _structure = {"device": dev, "port_id": port,
                                      "attributes": attributes}

                        portlist.append(_structure)

            return portlist





        if device is not None and port is not None:
            querystring = "device:" + str(device) + ":" + str(port)
            queryresult = self.client.keys.query(prefix=querystring)

            portlist = []
            for thing in queryresult:
                if isinstance(thing, list):
                    keys = thing
                    for k in keys:
                        _dev_temp = k.name
                        dev = _dev_temp.split(':')[1]
                        attributes = json.loads(k.value)
                        self._logger.info("ATTRIBUTES: " + str(attributes))

                        _structure = {"device": dev, "port_id": port,
                                      "attributes": attributes}

                        portlist.append(_structure)

            return portlist

    def setkvpair(self, key, data):
        """Set KV data using key and data."""
        string_data = json.dumps(data)
        self.client.keys.update(KeyValuePair(name=str(key),
                                             value=str(string_data)))

    def deletekvpair(self, key):
        """Set KV data using key and data."""
        self.client.keys.delete(KeyValuePair(name=str(key)))

    # <--------------- Serialise / De-Serialise Helpers ------->

    def run(self):

        # <------------------------------------------------------->
        # GET FUNCTION HANDLER FOR DEVICE
        @self.app.route("/v1/device/", methods=['GET'])
        def get():
            # Call getkvdata with no device or port
            return_data = self.getkvdata()

            return jsonify(return_data), 200, None

        # <------------------------------------------------------->
        # GET FUNCTION HANDLER FOR DEVICE/{DEVICE_ID}

        @self.app.route("/v1/device/<device_id>", methods=['GET'])
        def getid(device_id):
            return_data = self.getkvdata(device_id, None)
            return jsonify(return_data), 200, None

        # <------------------------------------------------------->
        # GET FUNCTION HANDLER FOR DEVICE/<device_id>/ports
        @self.app.route("/v1/device/<device_id>/port/<port>",
                        methods=['GET'])
        def getportid(device_id, port):
            return_data = self.getkvdata(device_id, port)
            return jsonify(return_data), 200, None

        # <------------------------------------------------------->
        # POST FUNCTION HANDLER FOR DEVICE/<device_id>/ports
        @self.app.route("/v1/device/<device_id>/port/<port>",
                        methods=['POST'])
        def postportid(device_id, port):
            """
            Note - this method does not allow to change port kind.

            If you have created a trunk port, that's what you're stuck with.

            Delete the port keys and start again if you want to change to an
            access port.
            """

            # Get the JSON for the request
            req_json = request.json

            # Set up initial data
            return_data = req_json

            # Get key from KV store for device
            k = self.getkvdata(device_id, port)

            if k:
                for data in k:
                    attributes = data['attributes']

                # Check if enforced appears
                if 'enforced' in req_json:
                    attributes['enforced'] = req_json['enforced']

                # Check if VLANs appear
                if 'vlan' in req_json:
                    # Check if any new VLANS appear
                    new_vlans = req_json['vlan']

                    if 'vlan' not in attributes:
                        attributes['vlan'] = []

                    old_vlans = attributes['vlan']

                    # Check if in the NEW_VLANS list there is one that isn't
                    # in OLD_VLANS

                    new_vlan_list = list(set(new_vlans) - set(old_vlans))

                    self._logger.info("VLANS TO BE ADDED: "
                                      + str(new_vlan_list))

                    # Add new vlans to old_list
                    for vlan in new_vlan_list:
                        attributes['vlan'].append(vlan)

                    self._logger.info("Attribute VLAN List: "
                                      + str(attributes))

                # Now let's check the description
                if 'description' in req_json:
                    if attributes['description'] != req_json['description']:
                        attributes['description'] = req_json['description']

                # We've fiddled, let's change executed to false
                attributes['executed'] = False

                # Now finalise the attributes as return_data
                return_data = attributes

            # Do some sanity setting on attributes like executed and enforced
            if not k:
                return_data['executed'] = False
                if 'enforced' not in return_data:
                    return_data['enforced'] = False

                if 'kind' not in return_data:
                    return jsonify("Error, must include 'kind'"), 400, None

            dev_id = "device:" + device_id + ":" + port
            self.setkvpair(dev_id, return_data)

            return jsonify(return_data), 201, None

        # <------------------------------------------------------->
        # DELETE FUNCTION HANDLER FOR DEVICE/<device_id>/ports
        @self.app.route("/v1/device/<device_id>/port/<port>",
                        methods=['DELETE'])
        def deleteportid(device_id, port):

            # Get the JSON for the request
            req_json = request.json

            # Get key from KV store for device
            k = self.getkvdata(device_id, port)

            if k:
                for data in k:
                    attributes = data['attributes']

                # If req_json is empty
                if not req_json:
                    dev_id = "device:" + str(device_id) + ":" + str(port)
                    self.deletekvpair(dev_id)
                    return jsonify("Deleted port: " + str(dev_id)), 201, None

                # If 'vlan' in request
                if 'vlan' in req_json:

                    # Check if any new VLANS appear
                    vlans_to_delete = req_json['vlan']

                    if 'vlan' not in attributes:
                        attributes['vlan'] = []

                    old_vlans = attributes['vlan']

                    # Check if in the NEW_VLANS list there is one that isn't
                    # in OLD_VLANS

                    new_vlan_list = list(set(old_vlans) - set(vlans_to_delete))

                    self._logger.info("VLANS TO BE DELETED: "
                                      + str(vlans_to_delete))

                    # Add new vlans to old_list
                    for vlan in new_vlan_list:
                        attributes['vlan'] = []
                        attributes['vlan'].append(vlan)

                    # VLAN list is empty
                    if not new_vlan_list:
                        attributes['vlan'] = []

                    self._logger.info("Attribute VLAN List: "
                                      + str(attributes))

                    # We've fiddled about, let's change execution
                    attributes['executed'] = False

                    # Now finalise the attributes as return_data
                    return_data = attributes

                    dev_id = "device:" + device_id + ":" + port
                    self.setkvpair(dev_id, return_data)

                    return jsonify(return_data), 201, None

            # Default response
            return jsonify(), 201, None

        # <------------------------------------------------------->
        # PUSH FUNCTION HANDLER FOR DEVICE/{DEVICE_ID}

        @self.app.route("/v1/push/", methods=['POST'])
        def postpush():
            # self._logger.info(request.json)
            return jsonify(), 204, None

        # <------------------------------------------------------->

        self.app.run(debug=True,
                     host=self._sensor_listen_ip,
                     port=int(self._sensor_listen_port))

        # <------------------------------------------------------->

    # You might be tempted to delete the unused methods.
    # Don't! It will fail validation for the runner.

    def setup(self):
        pass

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

    def _process_request(self, operation, device, port_id, vlan, desc, kind):
        """
        Simple method that dispatches a Trigger.

        operation:
            set:            set port parameters
            delete:         remove port parameters
            clear:          clear down port parameters and shut down
        device:             device in question
        port_id:            port in question
        vlan: []        List of vlans
        desc:    Description of port
        kind: (enum)
            enum:
                "trunk"
                "access"

        """
        payload = {"operation": operation,
                   "device": device,
                   "port_id": port_id,
                   "vlan": vlan,
                   "desc": desc,
                   "kind": kind}

        self._sensor_service.dispatch(trigger=self.receivedcall,
                                      payload=payload)
        return
