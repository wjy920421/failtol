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
    data["path"]   = 'create'
    data["query"] = {}

    if not id:
        data["query"]["id"]   = id
        
    if not activities:
        data["activities"] = activities


    req = json.dumps(data)
    m = Message()
    m.set_body(req)

    sqs.write(m)

    response.status = 202
    return req
