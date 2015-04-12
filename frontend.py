#!/usr/bin/env python

'''
  Front end Web server for final assignment, CMPT 474.
'''

# Library packages
import os
import sys
import json
import os.path
import utils

# Installed packages
import boto.sqs
import boto.sqs.message

from boto.sqs.message import Message
from bottle import route, run, request, response, abort, default_app

AWS_REGION = "us-west-2"
MAX_SECONDS = 180
PORT = 8080

global QUEUE_IN = test#sys.argv[1]   ***NEED TO FIX THIS!!!*** set_aws_envkeys file does not pass our arguments. Temp fix hardcoded queue name

conn = boto.sqs.connect_to_region(AWS_REGION)
    if conn == None:
        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(AWS_REGION))
        sys.exit(1)

def _response():
    return{
        "data" :{
            "type": "Notification",
            "msg" :  "Accepted"
        }
    }
def delete():
    userID = request.query.get('id')
    username = request.query.get('name')

    req = {'data':{
            'type'       : 'person',
            'id'         : userID,
            'name'       : username,
            }}

    req = json.dumps(request_json)
    print _response()

    my_queue = conn.get_queue(QUEUE_IN)
    m = boto.sqs.message.Message()
    m.set_body(req)
    my_queue.write(m)

    response.status = 202
    return _response
    

app = default_app()
run(app, host="localhost", port=PORT)