import create as api_create
import delete as api_delete
import retrieve as api_retrieve
import add_activities as api_add_activities
import utils

import boto
import boto.dynamodb2
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table

import time
import json
import random

import config


class DynamoDBManager():
    def __init__(self, table_name, aws_region, write_cap=10, read_cap=10):
        self.TABLE_NAME = table_name
        self.REGION = aws_region
        self.WRITE_CAP = write_cap
        self.READ_CAP = read_cap
        self.create_table()
        print 'Table "%s" has been created.' % self.TABLE_NAME

    def execute(self, request_json):
        request = json.loads(request_json)

        request_path = request['path']
        request_query = request['query']
        if request_path == 'create':
            response_json = self.do_create(request_query.get('id',None), request_query.get('name',None), request_query.get('activities',[]))
        elif request_path == 'delete':
            response_json = self.do_delete(request_query.get('id',None), request_query.get('name',None))
        elif request_path == 'retrieve':
            response_json = self.do_retrieve(request_query.get('id',None), request_query.get('name',None))
        elif request_path == 'add_activities':
            response_json = self.do_add_activities(request_query.get('id',None), request_query.get('activities',[]))
        else:
            raise Exception('Invalid operation for DynamoDBManager')

        return response_json


    def get_table(self):
        return Table(
                self.TABLE_NAME,
                schema=[HashKey('id')],
                connection=boto.dynamodb2.connect_to_region(self.REGION),
                throughput={'read':self.READ_CAP, 'write':self.WRITE_CAP}
            )

    def create_table(self):
        try:
            table = Table.create(
                    self.TABLE_NAME,
                    schema=[HashKey('id')],
                    connection=boto.dynamodb2.connect_to_region(self.REGION),
                    throughput={'read':self.READ_CAP, 'write':self.WRITE_CAP}
                )
            return table
        except Exception, e:
            return self.get_table()

    def delete_table(self):
        table = self.get_table()
        try:
            table.delete()
            print 'Table "%s" has been deleted.' % self.TABLE_NAME
        except Exception, e:
            wait_time = random.uniform(0.5, 2.0)
            print 'Failed to delete table "%s". Re-Try it %s seconds later.' % (self.TABLE_NAME, wait_time)
            time.sleep(wait_time)
            try:
                table.delete()
                print 'Table "%s" has been deleted.' % self.TABLE_NAME
            except Exception, e:
                print str(e)

    def do_create(self, user_id, username, activities):
        table = self.get_table()
        return api_create.do_create(table, user_id, username, activities)

    def do_delete(self, user_id, username):
        table = self.get_table()
        return api_delete.do_delete(table, user_id, username)

    def do_retrieve(self, user_id, username):
        table = self.get_table()
        return api_retrieve.do_retrieve(table, user_id, username)

    def do_add_activities(self, user_id, add_activities):
        table = self.get_table()
        return api_add_activities.do_add_activities(table, user_id, add_activities)


