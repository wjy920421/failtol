#!/usr/bin/env python

'''
  Back end server for final assignment CMPT 474.
'''

# Library packages
import json
import sys

# Installed packages
import boto.sqs

from bottle import route, run, request, response, default_app

import config

QUEUE_OUT = sys.argv[1]
VISIBILITY_TIMEOUT_S = 20

try:
    conn = boto.sqs.connect_to_region(config.AWS_REGION)
    if conn == None:
        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(config.AWS_REGION))
        sys.exit(1)

    '''
      EXTEND:
      Add code to open the output queue.
    '''
    #conn.create_queue(QUEUE_OUT)
    out_q = conn.get_queue(QUEUE_OUT)

except Exception as e:
    sys.stderr.write("Exception connecting to SQS\n")
    sys.stderr.write(str(e))
    sys.exit(1)

@route('/')
def app():
    '''
      EXTEND:
      Add code to read a message from the output queue into `m`.
      Put the message body in `resp`.
    '''
    print("Reading from output queue...")
    msg = out_q.read(VISIBILITY_TIMEOUT_S, config.MAX_WAIT_S_BACK)


    if msg == None:
        response.status = 204 # "No content"
        return ''
    else:
  		msg_body = msg.get_body()
  		print msg_body
  		converted_msg = json.loads(msg_body)
  		response.status = int(converted_msg['HTTP_status'])
  		resp = converted_msg['HTTP_response']

  		out_q.delete_message(msg)
  		return resp

app = default_app()
run(app, host=config.DEFAULT_SUBSCRIBE_TO, port=config.PORT_BACK)