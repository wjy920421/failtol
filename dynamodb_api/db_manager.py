import create as api_create
import delete as api_delete
import retrieve as api_retrieve
import add_activities as api_add_activities
import utils

import boto
import boto.dynamodb2
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table

import config


class DynamoDBManager():
    def __init__(self, table_name, aws_region, write_cap=10, read_cap=10):
        self.TABLE_NAME = table_name
        self.REGION = aws_region
        utils.create_table()

    def get_table():
        return Table(self.TABLE_NAME, connection=boto.dynamodb2.connect_to_region(self.REGION))

    def create_table():
        try:
            table = Table.create(self.TABLE_NAME, schema=[HashKey('id')], connection=boto.dynamodb2.connect_to_region(self.REGION))
            return table
        except Exception, e:
            return get_table()

    def delete_table():
        table = get_table()
        try:
            table.delete()
            return 'Table is deleted.'
        except Exception, e:
            return ''

    def do_create(user_id, username, activities):
        table = self.get_table()
        return api_create.do_create(table, user_id, username, activities)

    def do_delete(user_id, username):
        table = self.get_table()
        return api_delete.do_delete(table, user_id, username)

    def do_retrieve(user_id, username):
        table = self.get_table()
        return api_retrieve.do_retrieve(table, user_id, username)

    def do_add_activities(user_id, add_activities):
        table = self.get_table()
        return api_add_activities.do_add_activities(table, user_id, add_activities)


