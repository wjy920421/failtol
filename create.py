#!/usr/bin/env python

'''
  Create for final assignment, CMPT 474.
'''

#Library packages
import json


import boto.sqs
import boto.sqs.message
from boto.sqs.message import Message


def do_create(accID, accName, activities, response, sqs):
    
    activities_str = str(activities)
    activitiesLst = [] if activities_str is None else [act for act in activities_str.split(',') if act != '']
    
    data = {}
    data["path"]   = 'create'
    data["query"] = {}

    data["query"]["id"] = str(accID)
    data["query"]["name"] = str(accName)
    data["query"]["activities"] = activitiesLst

    req = json.dumps(data)
    m = Message()
    m.set_body(req)

    sqs.write(m)

    response.status = 202
    return req
