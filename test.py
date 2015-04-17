#!/usr/bin/env python

'''
  Unit test module for servers
'''

import os
import json
import time
import boto
import unittest
import subprocess

import config
import db



class TestModule(unittest.TestCase):
    # Test case for db 
    def test_db_single_instance(self):
        # Start a db instance
        queue_in_name = 'TEAM_LOADBALANCE_IN_TEST'
        queue_out_name = 'TEAM_LOADBALANCE_OUT_TEST'
        aws_region = 'us-west-2'

        conn = boto.sqs.connect_to_region(aws_region)
        assert conn is not None

        queue_in = conn.create_queue(queue_in_name)
        queue_out = conn.create_queue(queue_out_name)
        FNULL = open(os.devnull, 'w')
        p = subprocess.Popen(['./db.py', 'cloudsmall1.cs.surrey.sfu.ca', 'DB1', 'DB1', '', '7777', 'localhost', queue_in_name, queue_out_name, '10', '10'], env=os.environ.copy(), stdout=FNULL, stderr=subprocess.STDOUT)

        time.sleep(2)

        def dict_to_msg(d):
            msg = boto.sqs.message.Message()
            msg.set_body(json.dumps(d))
            return msg

        queue_in.write(dict_to_msg({"path": "create", "query": {"id": "1", "name": "Mac", "activities": ["hello", "haha"]}}))
        queue_in.write(dict_to_msg({"path": "create", "query": {"id": "1", "name": "Mac", "activities": ["hello", "haha"]}}))
        queue_in.write(dict_to_msg({"path": "create", "query": {"id": "1", "name": "Mac", "activities": ["hello", "haha", "hi"]}}))
        queue_in.write(dict_to_msg({"path": "retrieve", "query": {"id": "1"}}))
        queue_in.write(dict_to_msg({"path": "add_activities", "query": {"id": "1", "activities": ["hello", "hi"]}}))
        queue_in.write(dict_to_msg({"path": "retrieve", "query": {"id": "1"}}))
        queue_in.write(dict_to_msg({"path": "delete", "query": {"id": "1"}}))
        queue_in.write(dict_to_msg({"path": "retrieve", "query": {"id": "1"}}))

        time.sleep(5)

        self.assertEqual(queue_out.read().get_body(), json.dumps({'data':{'type':'person','id':'1','links':{'self':'http://localhost:8080/retrieve?id=1'}}}))
        self.assertEqual(queue_out.read().get_body(), json.dumps({'data':{'type':'person','id':'1','links':{'self':'http://localhost:8080/retrieve?id=1'}}}))
        self.assertEqual(queue_out.read().get_body(), json.dumps({"errors":[{"id_exists":{"status":"400","title":"id already exists","detail":{"name":"Mac","activities":["hello","haha"]}}}]}))
        self.assertEqual(queue_out.read().get_body(), json.dumps({'data':{'type':'person','id':"1",'name':"Mac",'activities':list(set(["hello","haha"]))}}))
        self.assertEqual(queue_out.read().get_body(), json.dumps({'data':{'type':'person','id':"1",'added:':["hi"]}}))
        self.assertEqual(queue_out.read().get_body(), json.dumps({'data':{'type':'person','id':"1",'name':"Mac",'activities':list(set(["hello","haha","hi"]))}}))
        self.assertEqual(queue_out.read().get_body(), json.dumps({'data':{'type':'person','id':"1",'name':"Mac"}}))
        self.assertEqual(queue_out.read().get_body(), json.dumps({'errors':[{'not_found':{'id':'1'}}]}))
        self.assertEqual(queue_out.read(), None)

        p.terminate()
        conn.delete_queue(queue_in_name)
        conn.delete_queue(queue_out_name)


if __name__ == '__main__':
    unittest.main()


