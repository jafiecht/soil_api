#First, we import the task id provided from the node script
############################################################################
import sys
#taskID = sys.argv[1]
taskID = '5c5fc9c9-c664-484d-9c2e-468d269527f2'


#Maybe return something to the script, so it knows things are running?
############################################################################
#print('Task : ' + taskID)


#Get and prep the data from the server
############################################################################
from pymongo import MongoClient
import config
import pprint

client = MongoClient(config.mongoURI)
db = client['soil-dev']
tasks = db.tasks
task = tasks.find_one({'id': taskID})
data = {
  'points': task['points'],  
  'boundary': task['boundary'],
  'id': task['id']  
}

#Convert polygon coords to float
for fIndex, feature in enumerate(data['boundary']['features']):
  data['boundary']['features'][fIndex]['properties'] = {}
  for lrIndex, linearRing in enumerate(feature['geometry']['coordinates']):
    for vIndex, vertex in enumerate(linearRing):
      for cIndex, coordinate in enumerate(vertex):
        data['boundary']['features'][fIndex]['geometry']['coordinates'][lrIndex][vIndex][cIndex] = float(coordinate)

#Convert point coords to float
for fIndex, feature in enumerate(data['points']['features']):
  for cIndex, coordinate in enumerate(feature['geometry']['coordinates']):
    data['points']['features'][fIndex]['geometry']['coordinates'][cIndex] = float(coordinate)

#Convert point property of interest to float
for fIndex, feature in enumerate(data['points']['features']):
  data['points']['features'][fIndex]['properties']['value'] = float(data['points']['features'][fIndex]['properties']['value'])


#Push to the script
############################################################################
import subprocess
import os
import shutil
#Make the process directory
subprocess.call('mkdir ' + data['id'] + '/', shell=True)
subprocess.call('mkdir ' + data['id'] + '/rootdata', shell=True)
subprocess.call('mkdir ' + data['id'] + '/topo', shell=True)
subprocess.call('mkdir ' + data['id'] + '/individuals', shell=True)
subprocess.call('mkdir ' + data['id'] + '/buffers', shell=True)
subprocess.call('mkdir ' + data['id'] + '/topo/curvatures', shell=True)

import root
response = root.validate_predict(data)

print('\n   Response: ', response)

#tasks.update_one({'id': taskID}, {"$set": task}, upsert=False)

#Remove process directory
if os.path.isdir(data['id']):
  shutil.rmtree( data['id'])


#import json
#rawInput = open('data/apicall/sparse_object.json')
#data = json.load(rawInput)



