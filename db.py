#!/usr/bin/env python

import boto.sqs
import boto.sqs.message

import zmq

import kazoo.exceptions
import kazooclientlast

import sys
import json
import time
import random
import signal
import os.path
import argparse
import contextlib

import config
import gen_ports



MAX_WAIT_S = 20 # SQS sets max. of 20 s
DEFAULT_VIS_TIMEOUT_S = 60

def build_parser():
    '''
    Parse the arguments of the script.
    '''
    parser = argparse.ArgumentParser(description="Web server demonstrating final project technologies")
    parser.add_argument("zkhost", help="ZooKeeper host string (name:port or IP:port, with port defaulting to 2181)")
    parser.add_argument("web_port", type=int, help="Web server port number", nargs='?', default=8080)
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

def main():
    '''
    Entry of the db instance.
    '''

    # Parse the arguments
    parser = build_parser()
    args = parser.parse_args()

    # Load settings from arguments
    zkhost              = args.zkhost
    instance_port       = args.web_port
    instance_name       = args.name
    instances           = args.instances_list.split(',')
    instances_num       = len(instances)
    proxied_instances   = args.proxied_instances_list.split(',') if args.proxied_instances_list != '' else []
    base_port           = args.base_port
    sub_to_name         = args.sub_to_name
    queue_in_name       = args.sqs_in
    queue_out_name      = args.sqs_out
    write_cap           = args.write_cap
    read_cap            = args.read_cap

    # Create the SQS-in and SQS-out queues. 
    try:
        conn = boto.sqs.connect_to_region(config.AWS_REGION)
        if conn is None:
            sys.stderr.write("Could not connect to AWS region '{0}'\n".format(config.AWS_REGION))
            sys.exit(1)
        queue_in = conn.create_queue(queue_in_name)
        queue_out = conn.create_queue(queue_out_name)

    except Exception as e:
        sys.stderr.write("Exception connecting to SQS\n")
        sys.stderr.write(str(e))
        sys.exit(1)

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

        # Create the sequence counter.
        seq_num = kz.Counter(config.SEQUENCE_OBJECT)

        # Process requests from SQS-in

        while True:
            seq_num += 1
            print "seq_num = %d" % seq_num.last_set
            time.sleep(2)

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


