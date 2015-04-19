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

    id            = str(accID)
    username      = str(accName)
    activities_str = str(activities)
    
    activitiesLst = [] if activities_str is None else [act for act in activities_str.split(',') if act != '']
    
    data = {}
    data["path"]   = 'create'
    data["query"] = {}

    if id:
        data["query"]["id"]   = id
        
    if activities_str:
        data["activities"] = activitiesLst
    
    data = {}
    data["path"]   = 'create'
    data["query"] = {}

    if id:
        data["query"]["id"]   = id
        
    if username:
        data["query"]["name"] = username

    if activities:
        data["query"]["activities"] = activitiesLst


    req = json.dumps(data)
    m = Message()
    m.set_body(req)

    sqs.write(m)

    response.status = 202
    return req
