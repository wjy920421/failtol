#!/usr/bin/env python

'''
  Worker task for CMPT 474 Exercise 6.

  Read requests from input queue, process them, and send results to the
  output queue.

  Queues are AWS SQS.
'''

# Standard libraries
import time
import json
import random

# Installed packages
import boto.sqs
import boto.sqs.message

AWS_REGION = "us-west-2"
QUEUE_IN = "ex6_in"
QUEUE_OUT = "ex6_out"
MAX_WAIT_S = 20 # SQS sets max. of 20 s
DEFAULT_VIS_TIMEOUT_S = 60 

try:
    conn = boto.sqs.connect_to_region(AWS_REGION)
    if conn == None:
        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(AWS_REGION))
        sys.exit(1)

    '''
      EXTEND:
      Add code to create the two queues.
    '''
    queue_in = conn.create_queue(QUEUE_IN)
    queue_out = conn.create_queue(QUEUE_OUT)

except Exception as e:
    sys.stderr.write("Exception connecting to SQS\n")
    sys.stderr.write(str(e))
    sys.exit(1)

while True:
    '''
      EXTEND:
      Replace the following line with code to read a message off the
      input queue, convert from JSON to a Python dict, and assign to
      `req`.
    '''
    queue_in = conn.get_queue(QUEUE_IN)
    request_messages = queue_in.get_messages()
    if len(request_messages) == 0:
        continue
    request_message = request_messages[0]
    request_json = request_message.get_body()
    queue_in.delete_message(request_message)
    try:
        req = json.loads(request_json)
    except Exception as e:
        continue

    actual_s = random.randint(0, req['s'])
    req['actual_s'] = actual_s
    print ("\nWorker received request {0} for {1}% for {2} seconds, actual wait {3}".
           format(req['id'], req['f'], req['s'], req['actual_s']))

    time.sleep(actual_s)

    '''
      EXTEND:
      Replace the following line with code to put the response on the
      output queue, in JSON representation.
    '''
    out_json = json.dumps(req)
    out_message = boto.sqs.message.Message()
    out_message.set_body(out_json)
    queue_out = conn.get_queue(QUEUE_OUT)
    queue_out.write(out_message)
    print "Request inserted into output queue."

