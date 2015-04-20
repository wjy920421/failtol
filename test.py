#!/usr/bin/env python

'''
  Unit test module for servers
'''

import os
import json
import time
import boto
import boto.sqs
import requests
import unittest
import subprocess

import config
import db



class TestModule(unittest.TestCase):
    # Test cases for backend
    def test_backend_empty(self):
        FNULL = open(os.devnull, 'w')
        p = subprocess.Popen(['./backend.py', 'TEAM_LOADBALANCE_OUT_TEST'], env=os.environ.copy(), stdout=FNULL, stderr=subprocess.STDOUT)

        time.sleep(1)

        # Try getting messages from backend
        r = requests.get('http://localhost:8081')
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.text, '')

        # Terminate backend
        p.terminate()

    def test_backend_not_empty(self):
        FNULL = open(os.devnull, 'w')
        p = subprocess.Popen(['./backend.py', 'TEAM_LOADBALANCE_OUT_TEST'], env=os.environ.copy(), stdout=FNULL, stderr=subprocess.STDOUT)

        time.sleep(1)

        conn = boto.sqs.connect_to_region('us-west-2')
        queue_out = conn.get_queue('TEAM_LOADBALANCE_OUT_TEST')

        sample_dict = {'HTTP_response':{"errors": [{"not_found": {"id": "4"}}]}, 'HTTP_status':404}
        sample_json = json.dumps(sample_dict)
        sample_msg = boto.sqs.message.Message()
        sample_msg.set_body(sample_json)
        queue_out.write(sample_msg)

        time.sleep(1)

        sample_dict_1 = {'HTTP_response':{"errors": [{"not_found": {"id": "5"}}]}, 'HTTP_status':403}
        sample_json_1 = json.dumps(sample_dict_1)
        sample_msg_1 = boto.sqs.message.Message()
        sample_msg_1.set_body(sample_json_1)
        queue_out.write(sample_msg_1)

        time.sleep(1)

        # Try getting messages from backend
        r = requests.get('http://localhost:8081')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.text, json.dumps(sample_dict['HTTP_response']))

        r = requests.get('http://localhost:8081')
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.text, json.dumps(sample_dict_1['HTTP_response']))

        r = requests.get('http://localhost:8081')
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.text, '')

        # Terminate backend
        p.terminate()

    # Test case for db 
    # def test_db_single_instance(self):
    #     # Start a db instance
    #     queue_in_name = 'TEAM_LOADBALANCE_IN_TEST'
    #     queue_out_name = 'TEAM_LOADBALANCE_OUT_TEST'
    #     aws_region = 'us-west-2'

    #     conn = boto.sqs.connect_to_region(aws_region)
    #     assert conn is not None

    #     queue_in = conn.create_queue(queue_in_name)
    #     queue_out = conn.create_queue(queue_out_name)
    #     FNULL = open(os.devnull, 'w')
    #     p = subprocess.Popen(['./db.py', 'cloudsmall1.cs.surrey.sfu.ca', 'DB1', 'DB1', '', '7777', 'localhost', queue_in_name, queue_out_name, '10', '10'], env=os.environ.copy(), stdout=FNULL, stderr=subprocess.STDOUT)

    #     time.sleep(2)

    #     def dict_to_msg(d):
    #         msg = boto.sqs.message.Message()
    #         msg.set_body(json.dumps(d))
    #         return msg

    #     queue_in.write(dict_to_msg({"path": "create", "query": {"id": "1", "name": "Mac", "activities": ["hello", "haha"]}}))
    #     time.sleep(1)
    #     queue_in.write(dict_to_msg({"path": "create", "query": {"id": "1", "name": "Mac", "activities": ["hello", "haha"]}}))
    #     time.sleep(1)
    #     queue_in.write(dict_to_msg({"path": "create", "query": {"id": "1", "name": "Mac", "activities": ["hello", "haha", "hi"]}}))
    #     time.sleep(1)
    #     queue_in.write(dict_to_msg({"path": "retrieve", "query": {"id": "1"}}))
    #     time.sleep(1)
    #     queue_in.write(dict_to_msg({"path": "add_activities", "query": {"id": "1", "activities": ["hello", "hi"]}}))
    #     time.sleep(1)
    #     queue_in.write(dict_to_msg({"path": "retrieve", "query": {"id": "1"}}))
    #     time.sleep(1)
    #     queue_in.write(dict_to_msg({"path": "delete", "query": {"id": "1"}}))
    #     time.sleep(1)
    #     queue_in.write(dict_to_msg({"path": "retrieve", "query": {"id": "1"}}))
    #     time.sleep(1)

    #     msg = queue_out.read(visibility_timeout=20)
    #     self.assertEqual(msg.get_body(), json.dumps({'data':{'type':'person','id':'1','links':{'self':'http://localhost:8080/retrieve?id=1'}}}))
    #     self.assertEqual(queue_out.count(), 7)
    #     msg.delete()
    #     time.sleep(1)
    #     msg = queue_out.read(visibility_timeout=20)
    #     self.assertEqual(msg.get_body(), json.dumps({'data':{'type':'person','id':'1','links':{'self':'http://localhost:8080/retrieve?id=1'}}}))
    #     self.assertEqual(queue_out.count(), 6)
    #     msg.delete()
    #     time.sleep(1)
    #     msg = queue_out.read(visibility_timeout=20)
    #     self.assertEqual(msg.get_body(), json.dumps({"errors":[{"id_exists":{"status":"400","title":"id already exists","detail":{"name":"Mac","activities":["hello","haha"]}}}]}))
    #     self.assertEqual(queue_out.count(), 5)
    #     msg.delete()
    #     time.sleep(1)
    #     msg = queue_out.read(visibility_timeout=20)
    #     self.assertEqual(msg.get_body(), json.dumps({'data':{'type':'person','id':"1",'name':"Mac",'activities':list(set(["hello","haha"]))}}))
    #     self.assertEqual(queue_out.count(), 4)
    #     msg.delete()
    #     time.sleep(1)
    #     msg = queue_out.read(visibility_timeout=20)
    #     self.assertEqual(msg.get_body(), json.dumps({'data':{'type':'person','id':"1",'added:':["hi"]}}))
    #     self.assertEqual(queue_out.count(), 3)
    #     msg.delete()
    #     time.sleep(1)
    #     msg = queue_out.read(visibility_timeout=20)
    #     self.assertEqual(msg.get_body(), json.dumps({'data':{'type':'person','id':"1",'name':"Mac",'activities':list(set(["hello","haha","hi"]))}}))
    #     self.assertEqual(queue_out.count(), 2)
    #     msg.delete()
    #     time.sleep(1)
    #     msg = queue_out.read(visibility_timeout=20)
    #     self.assertEqual(msg.get_body(), json.dumps({'data':{'type':'person','id':"1",'name':"Mac"}}))
    #     self.assertEqual(queue_out.count(), 1)
    #     msg.delete()
    #     time.sleep(1)
    #     msg = queue_out.read(visibility_timeout=20)
    #     self.assertEqual(msg.get_body(), json.dumps({'errors':[{'not_found':{'id':'1'}}]}))
    #     self.assertEqual(queue_out.count(), 0)
    #     msg.delete()
    #     time.sleep(1)

    #     p.terminate()
    #     conn.delete_queue(queue_in_name)
    #     conn.delete_queue(queue_out_name)
##    def test_frontend_retrieve(self):
##        FNULL = open(os.devnull, 'w')
##        p = subprocess.Popen(['./frontend.py', 'TEAM_LOADBALANCE_IN_TEST'], env=os.environ.copy(), stdout=FNULL, stderr=subprocess.STDOUT)
##
##        time.sleep(1)
##
##        # Try getting items
##        r = requests.get('http://localhost:8080/retrieve?id=34390&name=dsaa')
##        self.assertEqual(r.status_code, 204)
##        self.assertEqual(r.text, '')
##
##        # Terminate frontend
##        p.terminate()

    def test_frontend_create_querynotmatch_noactivities(self): #without activites
        FNULL = open(os.devnull, 'w')
        p = subprocess.Popen(['./frontend.py', 'TEAM_LOADBALANCE_IN_TEST'], env=os.environ.copy(), stdout=FNULL, stderr=subprocess.STDOUT)

        time.sleep(1)

        # Try creating items
        r = requests.get('http://localhost:8080/create?id=34390&name=dsaa')
        self.assertEqual(r.status_code, 400)

        # Terminate frontend
        p.terminate()

    def test_frontend_create_query_match_activities(self): #with activites
        FNULL = open(os.devnull, 'w')
        p = subprocess.Popen(['./frontend.py', 'TEAM_LOADBALANCE_IN_TEST'], env=os.environ.copy(), stdout=FNULL, stderr=subprocess.STDOUT)

        time.sleep(1)

        # Try creating items
        r = requests.get('http://localhost:8080/create?id=34390&name=dsaa&activities=a,b,c')
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.text, '')

        # Terminate frontend
        p.terminate()

    def test_frontend_delete_query_notmatch_id(self): #with wrong ID
        FNULL = open(os.devnull, 'w')
        p = subprocess.Popen(['./frontend.py', 'TEAM_LOADBALANCE_IN_TEST'], env=os.environ.copy(), stdout=FNULL, stderr=subprocess.STDOUT)

        time.sleep(1)

        # Try creating items
        r = requests.get('http://localhost:8080/delete?id=adsadasdas')
        self.assertEqual(r.status_code, 400)

        # Terminate frontend
        p.terminate()

    def test_frontend_delete_query_match_id(self): #with correct ID
        FNULL = open(os.devnull, 'w')
        p = subprocess.Popen(['./frontend.py', 'TEAM_LOADBALANCE_IN_TEST'], env=os.environ.copy(), stdout=FNULL, stderr=subprocess.STDOUT)

        time.sleep(1)

        # Try creating items
        r = requests.get('http://localhost:8080/delete?id=121')
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.text, '')

        # Terminate frontend
        p.terminate()

if __name__ == '__main__':
    unittest.main()


