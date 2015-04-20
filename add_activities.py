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

    activities_str = str(activities)
    activitiesLst = [] if activities_str is None else [act for act in activities_str.split(',') if act != '']
    
    data = {}
    data["path"] = 'add_activities'
    data["query"] = {}

    data["query"]["id"] = str(accID)
    data["query"]["activities"] = activitiesLst

    print data

    req = json.dumps(data)
    m = Message()
    m.set_body(req)

    sqs.write(m)

    response.status = 202
    return req
