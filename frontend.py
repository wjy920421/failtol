#!/usr/bin/env python

'''
  Front end Web server for final assignment, CMPT 474.
'''


import os
import sys
import json
import os.path

import boto.sqs
import boto.sqs.message
from boto.sqs.message import Message

from bottle import Bottle
from bottle import route, run, request, response, abort, default_app


from bottle import run, error, route

AWS_REGION = "us-west-2"
MAX_SECONDS = 180
PORT = 8080

QUEUE_IN = "djWang"#sys.argv[1]

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

"""
Delete REST API
"""
@route('/delete')
def delete():
    userID = request.query.get("id")
    username = request.query.get("name")
    
    data = {}
    data["type"] = 'person'
    data["id"]   = userID

    if not username:
        data["name"] = username

    request_json = {"data" : data}

    req = json.dumps(request_json)
    m = Message()
    m.set_body(req)

    my_queue = conn.get_queue(QUEUE_IN)
    my_queue.write(m)

    response.status = 202
    return _response()

"""
Create SQS connection
"""
try:
    conn = boto.sqs.connect_to_region(AWS_REGION)
    if conn == None:
        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(AWS_REGION))
        sys.exit(1)

    conn.create_queue(QUEUE_IN, MAX_SECONDS)
    
except Exception as e:
    sys.stderr.write("Exception connecting to SQS\n")
    sys.stderr.write(str(e))
    sys.exit(1)


app = default_app()
run(app, host="localhost", port=PORT)
