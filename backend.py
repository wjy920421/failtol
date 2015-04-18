#!/usr/bin/env python

'''
  Back end server for final assignment, CMPT 474.
'''

# Library packages
import time
#import json

# Installed packages
import boto.sqs

from bottle import route, run, request, response, default_app

import utils

QUEUE_OUT = "ex6_out"

try:
    conn = boto.sqs.connect_to_region(config.AWS_REGION)
    if conn == None:
        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(config.AWS_REGION))
        sys.exit(1)

    queue = conn.create_queue(QUEUE_OUT)

except Exception as e:
    sys.stderr.write("Exception connecting to SQS\n")
    sys.stderr.write(str(e))
    sys.exit(1)

def retrieve_message():
    queue = conn.get_queue(QUEUE_OUT)
    messages = queue.get_messages()
    if len(messages) == 0:
        return None
    message = messages[0]
    message_json = message.get_body()
    queue.delete_message(message)
    return message_json

@route('/')
def app():
    message_json = retrieve_message()

    if message_json is None:
        time.sleep(config.MAX_WAIT_S_BACK)
        message_json = retrieve_message()
        if message_json is None:
            response.status = 204 # "No content"
            return ''
        else:
            return message_json
    else:
        return message_json

app = default_app()
run(app, host=config.DEFAULT_SUBSCRIBE_TO , port=config.PORT_BACK)
