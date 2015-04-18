#!/usr/bin/env python

'''
  Retrieve for final assignment, CMPT 474.
'''

#Library packages
import json
import re

import boto.sqs
import boto.sqs.message
from boto.sqs.message import Message


QUERY_PATTERN_ID = "[id=0-9]+"
ID_PATTERN       = re.compile(QUERY_PATTERN_ID)

QUERY_PATTERN_NAME = "^(name=[a-zA-Z]+(_[a-zA-Z]+)*)$"
NAME_PATTERN       = re.compile(QUERY_PATTERN_NAME)

QUERY_PATTERN_ACTIVITIES = "^(id=[0-9]+)(&name=[a-zA-Z]+(_[a-zA-Z]+)*)(&activities=(([a-zA-Z]+([-_][a-zA-Z]+)*)(,([a-zA-Z]+([-_][a-zA-Z]+)*))*)*)?$"
ACT_PATTERN              = re.compile(QUERY_PATTERN_ACTIVITIES)

def do_retrieve(accID, accName, activities, response, sqs):

    id            = str(accID)
    username      = str(accName)
    lstActivities = str(activities)
    
    validId   = ID_PATTERN.match(id)
    validName = NAME_PATTERN.match(username)
    validActs = ACT_PATTERN.match(lstActivities)

    if not (validId or validName or validActs):
        response.status = 400
        abort(400,"Query did not match the pattern.")
    
    data = {}
    data["op"]   = 'retrieve'
    data["type"] = 'person'
    data["id"]   = id

    if not username:
        data["name"] = username

    if not activities:
        data["activities"] = activities

    request_json = {"data" : data}

    req = json.dumps(request_json)
    m = Message()
    m.set_body(req)

    sqs.write(m)

    response.status = 202
    return req
