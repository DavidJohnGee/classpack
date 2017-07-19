import sys

from st2actions.runners.pythonrunner import Action

class PubCredentials(Action):
    def __init__(self, config):
        super(PubCredentials, self).__init__(config)
        self.credentials = {}
        self.credentials['username'] = config['username']
        self.credentials['password'] = config['password']

    def run(self):
        return (True, self.credentials)
