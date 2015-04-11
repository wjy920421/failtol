#!/usr/bin/env python

import boto.sqs
import boto.sqs.message

import sys
import json
import time
import random
import signal
import os.path
import argparse
import contextlib

import config

AWS_REGION = "us-west-2"
QUEUE_IN = "ex6_in"
QUEUE_OUT = "ex6_out"
MAX_WAIT_S = 20 # SQS sets max. of 20 s
DEFAULT_VIS_TIMEOUT_S = 60

def build_parser():
    ''' Define parser for command-line arguments '''
    parser = argparse.ArgumentParser(description="Web server demonstrating final project technologies")
    parser.add_argument("zkhost", help="ZooKeeper host string (name:port or IP:port, with port defaulting to 2181)")
    parser.add_argument("web_port", type=int, help="Web server port number", nargs='?', default=8080)
    parser.add_argument("name", help="Name of this instance", nargs='?', default="DEFAULT_DB")
    parser.add_argument("instance_list", help="List of database instances", nargs='?', default="")
    parser.add_argument("proxy_list", help="List of instances to proxy, if any (comma-separated)", nargs='?', default="")
    parser.add_argument("base_port", type=int, help="Base port for publish/subscribe", nargs='?', default=config.DEFAULT_BASE_PORT)
    parser.add_argument("sub_to_name", help="Name of system to subscribe to", nargs='?', default=config.DEFAULT_SUBSCRIBE_TO)
    parser.add_argument("sqs_in", help="Name of the SQS-in queue", nargs='?', default=config.DEFAULT_SQS_IN)
    parser.add_argument("sqs_out", help="Name of the SQS-out queue", nargs='?', default=config.DEFAULT_SQS_OUT)
    parser.add_argument("write_cap", type=int, help="Write capacity of DynamoDB (writes/s)", nargs='?', default=config.DEFAULT_WRITE_CAPACITY)
    parser.add_argument("read_cap", type=int, help="Read capacity of DynamoDB (reads/s)", nargs='?', default=config.DEFAULT_READ_CAPACITY)
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        conn = boto.sqs.connect_to_region(config.AWS_REGION)
        if conn is None:
            sys.stderr.write("Could not connect to AWS region '{0}'\n".format(config.AWS_REGION))
            sys.exit(1)
        queue_in = conn.create_queue(args.sqs_in)
        queue_out = conn.create_queue(args.sqs_out)

    except Exception as e:
        sys.stderr.write("Exception connecting to SQS\n")
        sys.stderr.write(str(e))
        sys.exit(1)

    else:
        """
        while True:
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
            print ("\nWorker received request {0} for {1}% for {2} seconds, actual wait {3}".format(req['id'], req['f'], req['s'], req['actual_s']))

            time.sleep(actual_s)

            # Put the response on the output queue, in JSON representation.
            out_json = json.dumps(req)
            out_message = boto.sqs.message.Message()
            out_message.set_body(out_json)
            queue_out = conn.get_queue(QUEUE_OUT)
            queue_out.write(out_message)
            print "Request inserted into output queue."
        """



if __name__ == "__main__":
    main()


