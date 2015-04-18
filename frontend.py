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
from bottle import error, route

import config

import delete as delete_package
import retrieve as retrieve_package
import create as create_package

app = Bottle()

QUEUE_IN = "djflipout"#sys.argv[1] None
  

conn = boto.sqs.connect_to_region(config.AWS_REGION)

if conn == None:
    sys.stderr.write("Could not connect to AWS region '{0}'\n".format(config.AWS_REGION))
    sys.exit(1)

def _response():
    return{
        "data" :{
            "type": "Notification",
            "msg" :  "Accepted"
            }
        }

"""
Create REST API
"""
@route('/create')
def create(): 
    userID = request.query.get("id")
    username = request.query.get("name")
    activities = request.query.get("activities")

    user_id = request.query.get('id')
    username = request.query.get('name')
    my_queue = conn.get_queue(QUEUE_IN)

    response.status = 202
    create_package.do_create(user_id, username, activities, response, my_queue)
    return _response()

"""
Retrieve REST API
"""
@route('/retrieve')
def retrieve():
    userID = request.query.get("id")
    username = request.query.get("name")
    activities = request.query.get("activities")

    user_id = request.query.get('id')
    username = request.query.get('name')
    my_queue = conn.get_queue(QUEUE_IN)

    response.status = 202
    retrieve_package.do_retrieve(user_id, username, activities, response, my_queue)
    return _response()

"""
Delete REST API
"""
@route('/delete')
def delete():
    user_id = request.query.get('id')
    username = request.query.get('name')
    my_queue = conn.get_queue(QUEUE_IN)

    response.status = 202
    delete_package.do_delete(user_id, username, response, my_queue)
    return _response()

try:
    conn = boto.sqs.connect_to_region(config.AWS_REGION)
    if conn == None:
        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(config.AWS_REGION))
        sys.exit(1)

    conn.create_queue(QUEUE_IN, config.MAX_SECONDS)
    
except Exception as e:
    sys.stderr.write("Exception connecting to SQS\n")
    sys.stderr.write(str(e))
    sys.exit(1)


app = default_app()
run(app, host="localhost", port=config.PORT)
