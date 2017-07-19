# Class Demo Pack

### Contents

This pack is designed to exercise ST2 for class room based training.

It contains a number of branches, each of which contain different things.

__master branch__

This contains the starting point for the class. In this branch is just this README.md.

__class branch__

This contains all of the classroom based artefacts including rules, actions, action-chains and Mistral workflows. If you want to cheat, use this branch. If you accidentally blow your environment away, this branch will trigger memories of the training.

__bob_one branch__
This branch contains the customer example for Bob.

Bob wants to use a vRouter API to get interface information and integrate with ChatOps.

This branch contains a workflow and a custom action parser for the API.

__bob_two branch__
Bob wants more (who would have thought). 

Bob now wants to publish credentials into the workflow instead of someone passing them in.

This branch contains a new action which publishes credentials.


__alice_one branch__

Alice wants a place to create and delete VLANs using StackStorm.

This branch offers a sensor which is effectively a webserver.
This webserver offers POST, DELETE and GET verbs. Data created or deleted is via the KV store on StackStorm itself.


__alice_two branch__

Alice forgot, she wanted some rules to prove out the sensor is emitting triggers.

This branch includes rules!

__eve_one branch__

Eve wants to explore network automation specifically.

This branch contains a new workflow that uses components from the DC Fabrics pack.

This workflow specifically allows users of the Brocade VDX to create a point-to-point VNI and map to a VLAN. This VLAN is then presented to a trunked/not-trunked access port.

__eve_two branch__
Eve dropped the bombshell (shock horror) that she has CLI only devices in her network.
She wants to create a VLAN using Alice's sensor and have that push and validate a VLAN out to a Brocade MLXe.

This branch contains Eve's workflow for this. You will also need to install the CLICRUD pack and configure it appropriately for your environment.

#### Other Things

There is a directory containing experimental Python code snippets which may or may not be of use.

This directory is called `pythoncode`.

#### Usage

If you are using this pack, ensure that after each branch change, a reload of st2 is carried out.
`st2ctl reload`.

Some branches will also require a pack configuration step and a subsequent reload of st2 to put the configuration in to the database.
