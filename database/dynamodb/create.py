'''
  Web server for Assignment 3, CMPT 474.
'''

# Library packages
import json
import utils

import config


def do_create(table, user_id, username, activities):
    
    '''
      Basic server that returns the following JSON response
    '''

    data = {
        'id': user_id,
        'name': username,
        'activities': activities,
    }

    hasItem = table.has_item(id=user_id)
    sameItem = False
    if hasItem:
        user = table.get_item(id=user_id)
        if username == user['name']:
            if activities == [] and user['activities'] is None:
                sameItem = True
            if activities != [] and user['activities'] is not None and set(activities) == set(user['activities']):
                sameItem = True

    if hasItem == False or sameItem == True:
        try:
            table.put_item(data=data)
        except Exception, e:
            pass
            
        
        response_dict = {
            'data': {
                'type'  :   'person',
                'id'    :   user_id,
                'links' :   {
                    'self': 'http://localhost:8080' + '/retrieve?id=' + user_id,
                }
            }
        }
        
        response_json = json.dumps(response_dict)

        return response_json
    else:
        user = table.get_item(id=user_id)
        name1 = user['name']
        activities1 = user['activities']
        if activities1 is None:
            activities1 = []

        response_dict = {
            "errors": [{
                "id_exists": {
                    "status"    :   "400",
                    "title"     :   "id already exists",
                    "detail"    : {
                        "name"      : name1,
                        "activities": activities1,
                    }
                }
            }]
        }
        
    response_json = json.dumps(response_dict)

    return response_json



