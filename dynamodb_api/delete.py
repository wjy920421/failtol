import utils
import json


def do_delete(table, accID, accName):

    nullAccID = False
    accExist = False
    if accID is not None:
        accExist = table.has_item(id=accID)
    elif accName is not None:
        nullAccID = True
        for item in table.scan():
            if item['name'] == accName:
                accExist = True
                accID = item['id']
                break



    if(accExist): #looking at id first 
        data = table.get_item(id=accID)

        if(accName):    #check if user has entered in a name
            if(accName == data['name']):
                deleteSuceeded = table.delete_item(id=accID) #boolean value, delete by ID and name

                if(deleteSuceeded): #to see if delete actually works, handling another case is this acceptable?
                    req = {'data':{ #printing out
                    'type'       : 'person',
                    'id'         : data['id'],
                    'name'       : data['name'],          
                    }}

                else:
                    req ={'errors':[{
                    'not_found':{
                    'id':accID
                        }
                    }]}

            else:
                req ={'errors':[{
                'not_found':{
                'name':accName
                    }
                }]} 
        else: #no name was provided so delete by id
            deleteSuceeded = table.delete_item(id=accID) #boolean value, delete by ID and name

            if(deleteSuceeded): #to see if delete actually works, handling another case is this acceptable?
                req = {'data':{ #printing out
                'type'       : 'person',
                'id'         : data['id'],
                'name'       : data['name'],
                }}

            else:
                req ={'errors':[{
                    'not_found':{
                    'id':accID
                    }
                }]
                }
    else:
        if nullAccID:
            req ={'errors':[{
                    'not_found':{
                        'name':accName
                    }
                }]
            }
        else:
            req ={
                'errors':[{
                    'not_found':{
                        'id':accID
                    }
                }]
            }




    return json.dumps(req)
    