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
    
    data = {}
    data["path"] = 'delete'
    data["query"] = {}

    if accID:
        data["query"]["id"] = str(accID)

    if accName:
        data["query"]["name"] = str(accName)


    req = json.dumps(data)
    m = Message()
    m.set_body(req)

    sqs.write(m)

    response.status = 202
    return req
