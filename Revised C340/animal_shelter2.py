###########################################################################################
# Name                  : animal_shelter2.py
# Author                : Spencer Hayden
# Original Date         : 08/23/2020
# Revision Date         : 02/01/2022
# Version               : 2.0
# Description           : Python code that implements CRUD operations for MongoDB database.
# Allows ProjectTwoDashboard.ipynb to access database data and make inquiries and update 
# visual displays of data through UI. 
###########################################################################################

import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
from bson import json_util, ObjectId

# Creates AnimalShelter class to access MongoDB and perform CRUD operations
class AnimalShelter(object):
    # Initializing the MongoClient. This helps to access the MongoDB databases and collections.
    def __init__(self, username, password):
        # Retrieves user name and password from ProjectTwoDashboard.ipynb 
        self.client = MongoClient('mongodb://%s:%s@localhost:27017/admin' % (username, password))
        self.database = self.client['admin']

# Implements creation of entries into MongoDB.
    def create(self, data):
        if data is not None:
            self.database.animals.insert(data)
            return True      
        else:
            return False

# Implements reading of entries from MongoDB.
    def read(self, inquiry):
        if inquiry is not None:
            result = self.database.animals.find(inquiry,{"_id":False})
            return result
        else:
            raise Exception("Nothing to save, because data parameter is empty")

# Implements updating of entries in MongoDB.
    def update(self, inquiry, newValue):
        if inquiry is not None:
            result = self.database.animals.update_one(inquiry, newValue)
            doc = self.database.animals.find_one(inquiry)
            print(doc)
        else:
            raise Exception("Update not successful")
            
# Implements deleting of entries in MongoDB.
    def delete(self, inquiry):
        if inquiry is not None:
            result = self.database.animals.delete_one(inquiry)
            print(result)
            for x in self.database.animals.find():
                print(x)
        else:
            raise Exception("Delete not successful")
