#!/usr/bin/env python

'''
  Add_Activities for final assignment, CMPT 474.
'''

#Library packages
import json

import boto.sqs
import boto.sqs.message
from boto.sqs.message import Message

def do_add_activities(accID, activities, response, sqs):

    id            = str(accID)
    lstActivities = str(activities)
    
    data = {}
    data["op"]   = 'add_activities'
    data["type"] = 'person'
    data["id"]   = id

    if not activities:
        data["activities"] = activities

    request_json = {"data" : data}

    req = json.dumps(request_json)
    m = Message()
    m.set_body(req)

    sqs.write(m)

    response.status = 202
    return req
