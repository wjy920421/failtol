#!/usr/bin/env python

'''
  Back end server for final assignment CMPT 474.
'''

# Library packages
import json

# Installed packages
import boto.sqs

from bottle import route, run, request, response, default_app

import config

QUEUE_OUT = "ex6_out"
MAX_WAIT_S = 20 # SQS sets max. of 20 s


try:
    conn = boto.sqs.connect_to_region(config.AWS_REGION)
    if conn == None:
        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(config.AWS_REGION))
        sys.exit(1)

    '''
      EXTEND:
      Add code to open the output queue.
    '''
    conn.create_queue(QUEUE_OUT)

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
    q1 = conn.get_queue(QUEUE_OUT)
    m = q1.get_messages()
    m_read = m[0]
    m_read2 = m_read.get_body()


    #m = {'id': 0, 'f': 10, 's': 10, 'actual_s': 5}
    if m == None:
        response.status = 204 # "No content"
        return ''
    else:
      q1.delete_message(m_read)
      resp = json.loads(m_read2)
      #resp = {'id': 0, 'f': 10, 's': 10, 'actual_s': 5}
      return resp

app = default_app()
run(app, host=config.DEFAULT_SUBSCRIBE_TO, port=config.PORT_BACK)
