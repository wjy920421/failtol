import boto
import boto.dynamodb2
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table

import config


def get_table():
	return Table(config.TABLE_NAME, connection=boto.dynamodb2.connect_to_region(config.REGION))

def create_table():
	try:
		table = Table.create(config.TABLE_NAME, schema=[HashKey('id')], connection=boto.dynamodb2.connect_to_region(config.REGION))
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