#!/usr/bin/env python

'''
  Front end Web server for final assignment, CMPT 474.
'''


import os
import sys
import json
import os.path
import re

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

QUEUE_IN = sys.argv[1]

QUERY_PATTERN_ID = "[id=0-9]+"
ID_PATTERN       = re.compile(QUERY_PATTERN_ID)

QUERY_PATTERN_NAME = "^(name=[a-zA-Z]+(_[a-zA-Z]+)*)$"
NAME_PATTERN       = re.compile(QUERY_PATTERN_NAME)

QUERY_PATTERN_ACTIVITIES = "^(id=[0-9]+)(&name=[a-zA-Z]+(_[a-zA-Z]+)*)(&activities=(([a-zA-Z]+([-_][a-zA-Z]+)*)(,([a-zA-Z]+([-_][a-zA-Z]+)*))*)*)?$"
ACT_PATTERN              = re.compile(QUERY_PATTERN_ACTIVITIES)

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
    userID      = str(request.query.get("id"))
    username    = str(request.query.get("name"))
    activities  = str(request.query.get("activities"))
    
    my_queue    = conn.get_queue(QUEUE_IN)

    validId   = ID_PATTERN.match(userID)
    validName = NAME_PATTERN.match(username)
    validActs = ACT_PATTERN.match(activities)

    if not (validId or validName or validActs):
        response.status = 400
        abort(400,"Query did not match the pattern.")

    response.status = 202
    create_package.do_create(user_id, username, activities, response, my_queue)
    return _response()

"""
Retrieve REST API
"""
@route('/retrieve')
def retrieve():
    user_id     = str(request.query.get('id'))
    username    = str(request.query.get('name'))
    activities  = str(request.query.get("activities"))
    
    my_queue    = conn.get_queue(QUEUE_IN)
    
    validId   = ID_PATTERN.match(user_id)
    validName = NAME_PATTERN.match(username)
    validActs = ACT_PATTERN.match(activities)

    if not (validId or validName or validActs):
        response.status = 400
        abort(400,"Query did not match the pattern.")

    response.status = 202
    retrieve_package.do_retrieve(user_id, username, activities, response, my_queue)
    return _response()

"""
Delete REST API
"""
@route('/delete')
def delete():
    user_id = str(request.query.get('id'))
    username = str(request.query.get('name'))
    
    my_queue = conn.get_queue(QUEUE_IN)

    validId   = ID_PATTERN.match(user_id)
    validName = NAME_PATTERN.match(username)

    if not (validId or validName):
        response.status = 400
        abort(400,"Query did not match the pattern.")

    response.status = 202
    delete_package.do_delete(user_id, username, response, my_queue)
    return _response()


"""
SQS Connection
"""
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
run(app, host=config.DEFAULT_SUBSCRIBE_TO, port=config.PORT)
