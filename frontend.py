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

from frontend_api import delete as delete_package
from frontend_api import retrieve as retrieve_package
from frontend_api import create as create_package
from frontend_api import add_activities as add_activities_package

app = Bottle()

QUEUE_IN = sys.argv[1]

QUERY_PATTERN_ID = "^[0-9]+$" 
ID_PATTERN       = re.compile(QUERY_PATTERN_ID)

QUERY_PATTERN_NAME = "^([a-zA-Z]+(_[a-zA-Z]+)*)$"
NAME_PATTERN       = re.compile(QUERY_PATTERN_NAME)

QUERY_PATTERN_ACTIVITIES = "^([a-z_A-Z-]+(,[a-z_A-Z-]+)*)$"
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
    user_id        = request.query.get('id')
    username       = request.query.get('name')
    userActivities = request.query.get('activities')
    
    my_queue    = conn.get_queue(QUEUE_IN)

    if (user_id):
        validId = ID_PATTERN.match(user_id)
    else:
        validId = False

    if (username):
        validName = NAME_PATTERN.match(username)
    else:
        validName = False

    if (userActivities == ''):
        validActs = True
    elif (userActivities is not None):
        validActs = ACT_PATTERN.match(userActivities)
    else:
        validActs = False

    if not (validId and validName and validActs):
        response.status = 400
        abort(400,"Query did not match the pattern.")

    response.status = 202
    create_package.do_create(user_id, username, userActivities, response, my_queue)
    return _response()

"""
Retrieve REST API
"""
@route('/retrieve')
def retrieve():
    user_id     = request.query.get('id')
    username    = request.query.get('name')
    
    my_queue    = conn.get_queue(QUEUE_IN)

    if (user_id is not None):
        validId = ID_PATTERN.match(user_id)
    else:
        validId = True

    if (username is not None):
        validName = NAME_PATTERN.match(username)
    else:
        validName = True

    if not (validId and validName and (user_id is not None or username is not None)):
        response.status = 400
        abort(400,"Query did not match the pattern.")

    response.status = 202
    retrieve_package.do_retrieve(user_id, username, response, my_queue)
    return _response()

"""
Delete REST API
"""
@route('/delete')
def delete():
    user_id     = request.query.get('id')
    username    = request.query.get('name')
    
    my_queue    = conn.get_queue(QUEUE_IN)

    if (user_id is not None):
        validId = ID_PATTERN.match(user_id)
    else:
        validId = True

    if (username is not None):
        validName = NAME_PATTERN.match(username)
    else:
        validName = True

    if not (validId and validName and (user_id is not None or username is not None)):
        response.status = 400
        abort(400,"Query did not match the pattern.")

    response.status = 202
    delete_package.do_delete(user_id, username, response, my_queue)
    return _response()

"""
Add_activities REST API
"""
@route('/add_activities')
def add_activities():
    user_id        = request.query.get('id')
    userActivities = request.query.get('activities')
    
    my_queue    = conn.get_queue(QUEUE_IN)

    if (user_id):
        validId = ID_PATTERN.match(user_id)
    else:
        validId = False

    if (userActivities == ''):
        validActs = True
    elif (userActivities is not None):
        validActs = ACT_PATTERN.match(userActivities)
    else:
        validActs = False
        

    if not (validId and validActs):
        response.status = 400
        abort(400,"Query did not match the pattern.")

    response.status = 202
    add_activities_package.do_add_activities(user_id, userActivities, response, my_queue)
    return _response()


"""
SQS Connection
"""
try:
    conn = boto.sqs.connect_to_region(config.AWS_REGION)
    if conn == None:
        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(config.AWS_REGION))
        sys.exit(1)

    conn.create_queue(QUEUE_IN)
    
except Exception as e:
    sys.stderr.write("Exception connecting to SQS\n")
    sys.stderr.write(str(e))
    sys.exit(1)

app = default_app()
run(app, host=config.DEFAULT_SUBSCRIBE_TO, port=config.PORT)
