#!/usr/bin/env python

import boto.sqs
import boto.sqs.message

import sys
import json
import time
import random
import atexit
import signal
import os.path
import argparse
import threading

import config
from database.dynamodb.db_manager import DynamoDBManager
from database.zookeeper.zookeeper_client import ZookeeperClient
from database.pubsub.pubsub import PubSubManager



MAX_WAIT_S = 20 # SQS sets max. of 20 s
DEFAULT_VIS_TIMEOUT_S = 60

def build_parser():
    '''
    Parse the arguments of the script.
    '''
    parser = argparse.ArgumentParser(description="Web server demonstrating final project technologies")
    parser.add_argument("zkhost", help="ZooKeeper host string (name:port or IP:port, with port defaulting to 2181)")
    parser.add_argument("name", help="Name of this instance", nargs='?', default="DEFAULT_DB")
    parser.add_argument("instances_list", help="List of database instances", nargs='?', default="")
    parser.add_argument("proxied_instances_list", help="List of instances to proxy, if any (comma-separated)", nargs='?', default="")
    parser.add_argument("base_port", type=int, help="Base port for publish/subscribe", nargs='?', default=config.DEFAULT_BASE_PORT)
    parser.add_argument("sub_to_name", help="Name of system to subscribe to", nargs='?', default=config.DEFAULT_SUBSCRIBE_TO)
    parser.add_argument("sqs_in", help="Name of the SQS-in queue", nargs='?', default=config.DEFAULT_SQS_IN)
    parser.add_argument("sqs_out", help="Name of the SQS-out queue", nargs='?', default=config.DEFAULT_SQS_OUT)
    parser.add_argument("write_cap", type=int, help="Write capacity of DynamoDB (writes/s)", nargs='?', default=config.DEFAULT_WRITE_CAPACITY)
    parser.add_argument("read_cap", type=int, help="Read capacity of DynamoDB (reads/s)", nargs='?', default=config.DEFAULT_READ_CAPACITY)
    return parser




def setup_sqs(queue_in_name, queue_out_name):
    try:
        conn = boto.sqs.connect_to_region(config.AWS_REGION)
        if conn is None:
            sys.stderr.write("Could not connect to AWS region '{0}'\n".format(config.AWS_REGION))
            sys.exit(1)
        queue_in = conn.create_queue(queue_in_name)
        queue_out = conn.create_queue(queue_out_name)

        return conn

    except Exception as e:
        sys.stderr.write("Exception connecting to SQS\n")
        sys.stderr.write(str(e))
        sys.exit(1)

def subscribe(pubsub_manager):
    while not exit_signal:
        msg = pubsub_manager.subscribe()
        if msg is None:
            time.sleep(1)
            continue
        print "Subscribe:"
        print msg 

def main():
    '''
    Entry of the db instance.
    '''

    # Parse the arguments
    parser = build_parser()
    args = parser.parse_args()

    # Load settings from arguments
    zkhost              = args.zkhost
    instance_name       = args.name
    instances           = args.instances_list.split(',')
    instances_num       = len(instances)
    proxied_instances   = args.proxied_instances_list.split(',') if args.proxied_instances_list != '' else []
    base_port           = args.base_port
    sub_to_name         = args.sub_to_name
    QUEUE_IN_NAME       = args.sqs_in
    QUEUE_OUT_NAME      = args.sqs_out
    write_cap           = args.write_cap
    read_cap            = args.read_cap
    DYNAMODB_NAME       = config.BASE_DYNAMODB_NAME + instance_name

    # Initialize DynamoDB
    db_manager = DynamoDBManager(table_name=DYNAMODB_NAME, aws_region=config.AWS_REGION, write_cap=write_cap, read_cap=read_cap)
    print 'Table named "%s" has been created.' % DYNAMODB_NAME
    if config.DELETE_DYNAMODB_ON_EXIT:
        atexit.register(db_manager.delete_table)

    # Setup the SQS-in and SQS-out queues. 
    conn = setup_sqs(QUEUE_IN_NAME, QUEUE_OUT_NAME)

    # Open connection to ZooKeeper, and Setup Publish/Subscribe manager
    with ZookeeperClient(zkhost=zkhost, instance_name=instance_name, instances_num=instances_num, seq_obj_path=config.SEQUENCE_OBJECT, barrier_path=config.APP_DIR + config.BARRIER_NAME) as zk_client, \
         PubSubManager(instance_name=instance_name, instances=instances, proxied_instances=proxied_instances, sub_to_name=sub_to_name, base_port=base_port) as pubsub_manager:
        
        subscribe_thread = threading.Thread(target=subscribe, args=(pubsub_manager,))
        subscribe_thread.start()

        print "%s is now running...\n" % instance_name

        # Process requests from SQS-in
        """
        while True:
            zk_client.seq_num += 1
            print "seq_num = %d" % zk_client.seq_num.last_set
            time.sleep(1)
        """
        while True:
            # Get a message from the start point of the queue
            queue_in = conn.get_queue(QUEUE_IN_NAME)
            request_message = queue_in.read(visibility_timeout=config.DEFAULT_VISIBILITY_TIMEOUT)
            if request_message is None:
                time.sleep(1)
                continue

            # Convert the message to a dictionary
            request_json = request_message.get_body()
            print "Request received from SQS-in:"
            print request_json
            try:
                request_dict = json.loads(request_json)
            except Exception as e:
                print "Invalid Request."
                queue_in.delete_message(request_message)
                continue

            # Publish for synchronization
            pubsub_manager.publish(request_json)

            # Perform the operation as specified in the message
            response_json = db_manager.execute(request_dict)
            
            # Delete the message on success
            queue_in.delete_message(request_message)

            # Put the response on the output queue, in JSON representation.
            response_message = boto.sqs.message.Message()
            response_message.set_body(response_json)
            queue_out = conn.get_queue(QUEUE_OUT_NAME)
            queue_out.write(response_message)
            print "Response inserted into SQS-out:"
            print response_json


if __name__ == "__main__":
    try:
        global exit_signal
        exit_signal = False
        main()
    except KeyboardInterrupt:
        exit_signal = True
        print "EXIT_SIGNAL: shutting down all threads..."


