#!/usr/bin/env python

'''
  Delete for final assignment, CMPT 474.
'''

#Library packages
import json

import boto.sqs
import boto.sqs.message
from boto.sqs.message import Message


def do_delete(accID, accName, response, sqs):

    id       = str(accID)
    username = str(accName)
    
    data = {}
    data["path"]   = 'create'
    data["query"] = {}

    if not id:
        data["query"]["id"]   = id

    if not username:
        data["name"] = username


    req = json.dumps(data)
    m = Message()
    m.set_body(req)

    sqs.write(m)

    response.status = 202
    return req
