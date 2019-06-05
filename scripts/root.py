#This file makes predictions for all the training files
#then tests each prediction.

#Imports
import input_checker
import tile_selector
import curvatures
import rasterizer
import buffers
import stack
import export_functions
import metrics
import viewer
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
#from sklearn.ensemble import RandomForestRegressor
import shutil
import os
import subprocess
import json
import time

def validate_predict(inputObject):
  overall_start = time.time() 
 
  #Validate user input
  #############################################################
  #print('\n - Validating user input')
  start = time.time()
  try:
    status = input_checker.check(inputObject)
    if status != 'OK':
      return {'status': 400, 'message': status}
  except:
    return {'status': 500, 'message': 'Server failure while checking inputs'}
  #print('   Process time: ', time.time() - start)

  #Select raster tiles with field boundary
  #############################################################
  #print('\n - Downloading elevation data')
  start = time.time()
  try:
    status = tile_selector.getDEM(inputObject['id'])
    if status != 'OK':
      return {'status': 400, 'message': status}
  except:
    return {'status': 500, 'message': 'Server failure while retrieving elevation data'}
  #print('   Process time: ', time.time() - start)

  #Calculate topographic derivatives
  #############################################################
  #print('\n - Calculating slopes and curvatures')
  start = time.time()
  try:
    curvatures.generate_curvatures(inputObject['id'])
    topo_data = stack.return_topo(inputObject['id'])
  except:
    return {'status': 500, 'message': 'Server failure while calculating topographic derivatives'}
  #print('   Process time: ', time.time() - start)

  #Create rasterize the shapefile points
  #############################################################
  #print('\n - Rasterizing point data')
  start = time.time()
  try:
    rasterizer.rasterize(inputObject['id'])
    point_data = stack.return_points(inputObject['id'])
  except:
    return {'status': 500, 'message': 'Server failure while rasterizing point data'}
  #print('   Process time: ', time.time() - start)

  #Make buffer distance layers for each known point.
  #############################################################
  #print('\n - Creating buffer layers')
  start = time.time()
  try:
    buffers.make_buffers(inputObject['id'])
    buffer_data = stack.return_buffers(inputObject['id'])
  except:
    return {'status': 500, 'message': 'Server failure while creating point buffer data'}
  #print('   Process time: ', time.time() - start)

  #Test predictions
  #############################################################
  #print('\n - Testing model')
  start = time.time()
  try:
    scores = validate(point_data, topo_data, buffer_data)
  except:
    return {'status': 500, 'message': 'Server failure while testing predictions'}
  #print('   Process time: ', time.time() - start)

  #Make master prediction
  #############################################################
  #print('\n - Making final prediction')
  start = time.time()
  try:
    predictions = map_predictions(point_data, topo_data, buffer_data)
  except:
    return {'status': 500, 'message': 'Server failure while making predictions'}
  #print('   Process time: ', time.time() - start)

  #Get Template Data and write data out
  #############################################################
  #print('\n - Exporting prediction')
  start = time.time()
  try:
    raster_shape, geotrans, proj = stack.template(topo_data, inputObject['id'])
    bounds = export_functions.output_tif(predictions, raster_shape, geotrans, proj, inputObject['id'])
  except:
    return {'status': 500, 'message': 'Server failure while writing predictions to file'}
  #print('   Process time: ', time.time() - start)

  #Clean up temporary files  
  #############################################################
  #print('\n - Deleting files')
  #start = time.time()
  #try:
    #stack.cleanup()
  #except:
    #return {'status': 500, 'message': 'Server failure while removing temporary files'}
  #print('   Process time: ', time.time() - start)
  #print('   Overall: ', time.time() - overall_start)
  
  #Show prediction
  #############################################################
  #print('\n - Done')
  return {'status': 200, 'message': 'prediction made', 'scores': scores, 'bounds': bounds}

#This performs an n-fold cross validation test
def validate(point_data, topo, buffers):

  #Run the function for each filename
  #############################################################
  points = list(point_data.keys())
  value_pairs = list()
  iteration = 0
  length = len(points)
  for test_point in points: 

    #Take the validation point out of the training set
    #############################################################
    training_points = points.copy()
    training_points.remove(test_point)
    training_buffers = training_points
 
    #Assemble the training set
    #############################################################
    training_set = list()
    for training_point in training_points:
      obs = list()
      for feature in topo:
        obs.append(feature[point_data[training_point]['index']])
      for buffer_feature in training_buffers:
        obs.append(buffers[buffer_feature][point_data[training_point]['index']])
      obs.append(point_data[training_point]['value'])
      training_set.append(obs)

    #Assemble the test set
    #############################################################
    testing_set = list()
    obs = list()
    for feature in topo:
      obs.append(feature[point_data[test_point]['index']])
    for buffer_feature in training_buffers:
      obs.append(buffers[buffer_feature][point_data[test_point]['index']])
    testing_set.append(obs)

    #Generate Prediction
    #############################################################
    prediction = train_predict(training_set, testing_set) 
    
    value_pairs.append([point_data[test_point]['value'], prediction[0]])
        
    #Log Progress
    #############################################################
    iteration += 1
    #print(str(int(iteration/length*90)+5)+'%')

  scores = metrics.generate_metrics(value_pairs)

  #print('     R2 Score: ' + str(scores[0]))  
  #print('     RMSE: ' + str(scores[1]))  
  #print('     ME: ' + str(scores[2]))  
  #print('     MAE: ' + str(scores[3]))  
  #print('   test: ', {'R2': scores[0], 'RMSE': scores[1], 'ME': scores[2], 'MAE': scores[3]})
  return {'R2': scores[0], 'RMSE': scores[1], 'ME': scores[2], 'MAE': scores[3]}
  

def map_predictions(point_data, topo, buffers):
  
  #Define iterables
  #############################################################
  points = list(point_data.keys())
  training_buffers = points
  
  #Assemble the training set
  #############################################################
  training_set = list()
  for training_point in points:
    obs = list()
    for feature in topo:
      obs.append(feature[point_data[training_point]['index']])
    for buffer_feature in training_buffers:
      obs.append(buffers[buffer_feature][point_data[training_point]['index']])
    obs.append(point_data[training_point]['value'])
    training_set.append(obs)
  
  #Assemble the prediction set
  #############################################################
  feature_set = topo.copy()
  for buffer_feature in training_buffers:
    feature_set.append(buffers[buffer_feature])

  #Transform feature_set into 1-d lists
  #############################################################
  raster_shape = feature_set[0].shape
  stack = np.zeros(shape=((raster_shape[0]*raster_shape[1]), len(feature_set)))
  index = 0
  #Loop through all 3 dimensions
  for i in range(raster_shape[0]):
    for j in range(raster_shape[1]):
      for feature_index in range(len(feature_set)):
        #Assign values to the 2-d stack from the 3-d array set
        stack[index, feature_index] = feature_set[feature_index][i,j]
      index += 1

  #Generate Predictions
  #############################################################
  predictions = train_predict(training_set, stack.tolist()) 
  return predictions    

###############################################################
def train_predict(training_set, prediction_set):


  #Split the datasets into feature and value sets
  training_values = [row[-1] for row in training_set]
  training_features = [row[0:-1] for row in training_set]
 

  #Define the regressor parameters
  forest = ExtraTreesRegressor(max_depth=4, n_estimators=4000, min_samples_leaf=4, max_features=.5)
  #forest = RandomForestRegressor(max_depth=4, n_estimators=2000, min_samples_leaf=4, max_features=.5)

  #Fit the forest to the training data
  forest.fit(training_features, training_values)

  #Retrieve the feature importances
  #importances = pd.DataFrame(forest.feature_importances_, index = layers, columns = ['importance']).sort_values('importance', ascending=False)
  #print(importances.to_string())

  #Feed in the raw dataset feature to predict continous values
  predictions = forest.predict(prediction_set).tolist()

  return predictions

