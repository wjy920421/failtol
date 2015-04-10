import json
import utils


"""
Get item by id
"""

def do_retrieve(userID, userName):
            
    users = utils.get_table()

    #Check if the items exists in DB
    nullUserID = False
    userExist = False
    idExist = False
    if userID is not None:
        idExist = users.has_item(id=userID)
    elif userName is not None:
        nullUserID = True
        for item in users.scan():
            if item['name'] == userName:
                userExist = True
                userID = item['id']
                break
    
    if(idExist):
        data = users.get_item(id=userID)
        nameOfUser = data['name']
        
        if(userName == nameOfUser):
            userExist = True
        if(userName == None):
            userExist = True 

            

    #Retrieve by ID and name 
    if(userExist):
        data = users.get_item(id=userID)
        activities = data['activities']
        if activities is None:
            activities = []
        lstActivities = list(activities)

        req = {'data':{
            'type'       : 'person',
            'id'         : data['id'],
            'name'       : data['name'],
            'activities' : lstActivities
            }}
        
    elif(userName is not None and (idExist or nullUserID)):
        req ={'errors':[{
            'not_found':{
                'name':userName
                }
            }]
        }        

    else:
        req ={'errors':[{
            'not_found':{
                'id':userID
                }
            }]
        }

    return json.dumps(req)
    
