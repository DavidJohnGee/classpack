import sys

from st2actions.runners.pythonrunner import Action

class MyEchoAction(Action):
    def run(self, message):
	
        for m in message:
            print(m)   
 
        return (True, message)
