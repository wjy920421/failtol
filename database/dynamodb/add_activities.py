'''
  Web server for Assignment 3, CMPT 474.
'''

# Library packages
from boto.dynamodb2.exceptions import ConditionalCheckFailedException
import json
import utils
import time

def do_add_activities(table, user_id, add_activities):
    
    '''
      Basic server that returns the following JSON response
    '''
    status_code = 200

    hasItem = table.has_item(id=user_id)
    if (hasItem):
        # Keep looping until the transaction succeeds
        while(True):
            try:
                user = table.get_item(id=user_id)

                # take the union of the previous activity list and the new activity list
                prev_activities = user['activities']
                if prev_activities is None:
                    prev_activities = []
                new_activities = list(set(prev_activities) | set(add_activities))

                user['activities'] = new_activities
                user.partial_save()

                actual_added = []
                for act in add_activities:
                    if act not in prev_activities:
                        actual_added.append(act)

                request_json = {
                    'data': {
                        'type'   : 'person',
                        'id'     : user['id'],
                        'added:' : actual_added,
                    }
                }
                status_code = 200
                # finish adding activites and break out from the while loop
                break
            except ConditionalCheckFailedException:
                # Retry add activities if the exception is thrown
                print "Data is inconsistent! Retry after 1 second..."
                time.sleep(1)
    else:
        request_json = {
            'errors': [{
                'not_found' : {
                    'id': user_id
                }
            }]
        }
        status_code = 404

    request_json = {'HTTP_response':request_json, 'HTTP_status':status_code}
    req = json.dumps(request_json)
    return req
