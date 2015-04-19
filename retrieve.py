#!/usr/bin/env python

'''
  Retrieve for final assignment, CMPT 474.
'''

#Library packages
import json

import boto.sqs
import boto.sqs.message
from boto.sqs.message import Message

def do_retrieve(accID, accName, activities, response, sqs):

    id            = str(accID)
    username      = str(accName)
    lstActivities = str(activities)
    
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
