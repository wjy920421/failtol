#!/usr/bin/env python

'''
  Back end server for Exercise 6, CMPT 474.
'''

# Library packages
import time
#import json

# Installed packages
import boto.sqs

from bottle import route, run, request, response, default_app

AWS_REGION = "us-west-2"
QUEUE_OUT = "ex6_out"
MAX_WAIT_S = 20 # SQS sets max. of 20 s
PORT = 8081

try:
    conn = boto.sqs.connect_to_region(AWS_REGION)
    if conn == None:
        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(AWS_REGION))
        sys.exit(1)

    '''
      EXTEND:
      Add code to open the output queue.
    '''
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
    '''
      EXTEND:
      Add code to read a message from the output queue into `m`.
      Put the message body in `resp`.
    '''
    message_json = retrieve_message()

    if message_json is None:
        time.sleep(MAX_WAIT_S)
        message_json = retrieve_message()
        if message_json is None:
            response.status = 204 # "No content"
            return 'Queue empty\n'
        else:
            return message_json
    else:
        return message_json

app = default_app()
run(app, host="localhost", port=PORT)