#!/usr/bin/env python

import boto.sqs
import boto.sqs.message

import zmq

import kazoo.exceptions
from zookeeper import kazooclientlast

import sys
import json
import time
import random
import atexit
import signal
import os.path
import argparse
import contextlib

import config
import gen_ports

from dynamodb_api.db_manager import DynamoDBManager



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

@contextlib.contextmanager
def zmqcm(zmq_context):
    '''
    This function wraps a context manager around the zmq context, allowing the client to be used in a 'with' statement.
    '''
    try:
        yield zmq_context
    finally:
        print "Closing sockets"
        # The "0" argument destroys all pending messages immediately without waiting for them to be delivered
        zmq_context.destroy(0)

@contextlib.contextmanager
def kzcl(kz):
    '''
    This function wraps a context manager around the kazoo client, allowing the client to be used in a 'with' statement.
    '''
    kz.start()
    try:
        yield kz
    finally:
        print "Closing ZooKeeper connection"
        kz.stop()
        kz.close()

def setup_pub_sub(zmq_context, sub_to_name, pub_port, sub_ports, instance_name):
    '''
    Set up the publish and subscribe connections.
    '''

    # Open a publish socket.
    pub_socket = zmq_context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:{0}".format(pub_port))
    print "instance {0} binded on {1}".format(instance_name, pub_port)

    # Open subscribe sockets.
    sub_sockets = []
    for sub_port in sub_ports:
        sub_socket = zmq_context.socket(zmq.SUB)
        sub_socket.setsockopt(zmq.SUBSCRIBE, "")
        sub_socket.connect("tcp://{0}:{1}".format(sub_to_name, sub_port))
        sub_sockets.append(sub_socket)
        print "instance {0} connected to {1} on {2}".format(instance_name, sub_to_name, sub_port)

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

    # Open connection to ZooKeeper and context for zmq
    with kzcl(kazooclientlast.KazooClientLast(hosts=zkhost)) as kz, zmqcm(zmq.Context.instance()) as zmq_context:

        # Set up publish and subscribe sockets
        pub_port, sub_ports = gen_ports.gen_ports(base_port, instances, proxied_instances, instance_name)
        setup_pub_sub(zmq_context, sub_to_name, pub_port, sub_ports, instance_name)

        # Initialize sequence numbering by ZooKeeper
        try:
            kz.create(path=config.SEQUENCE_OBJECT, value="0", makepath=True)
        except kazoo.exceptions.NodeExistsError as nee:
            kz.set(config.SEQUENCE_OBJECT, "0") # Another instance has already created the node
                                         # or it is left over from prior runs

        # Wait for all DBs to be ready
        barrier_path = config.APP_DIR + config.BARRIER_NAME
        kz.ensure_path(barrier_path)
        b = kz.create(barrier_path + '/' + instance_name, ephemeral=True)
        while len(kz.get_children(barrier_path)) < instances_num:
            time.sleep(1)
        print "Past rendezvous"
        print "%s is now running...\n" % instance_name

        # Create the sequence counter.
        seq_num = kz.Counter(config.SEQUENCE_OBJECT)

        # Process requests from SQS-in
        """
        while True:
            seq_num += 1
            print "seq_num = %d" % seq_num.last_set
            time.sleep(2)
        """
        while True:
            # Get a message from the start point of the queue
            queue_in = conn.get_queue(QUEUE_IN_NAME)
            request_messages = queue_in.get_messages(num_messages=1, visibility_timeout=config.DEFAULT_VISIBILITY_TIMEOUT)
            if len(request_messages) == 0:
                time.sleep(1)
                continue

            # Convert the message to a dictionary
            request_message = request_messages[0]
            request_json = request_message.get_body()
            try:
                request_dict = json.loads(request_json)
            except Exception as e:
                queue_in.delete_message(request_message)
                continue

            # Perform the operation as specified in the message
            response_json = ''
            request_path = request_dict['path']
            request_query = request_dict['query']
            if request_path == 'create':
                response_json = db_manager.do_create(request_query['id'], request_query['name'], request_query['activities'])
            elif request_path == 'delete':
                response_json = db_manager.do_delete(request_query['id'], request_query['name'])
            elif request_path == 'retrieve':
                response_json = db_manager.do_retrieve(request_query['id'], request_query['name'])
            elif request_path == 'add_activities':
                response_json = db_manager.do_add_activities(request_query['id'], request_query['activities'])

            # Delete the message on success
            queue_in.delete_message(request_message)

            # Put the response on the output queue, in JSON representation.
            response_message = boto.sqs.message.Message()
            response_message.set_body(response_json)
            queue_out = conn.get_queue(QUEUE_OUT_NAME)
            queue_out.write(response_message)
            print "Response inserted into output queue."



if __name__ == "__main__":
    main()


