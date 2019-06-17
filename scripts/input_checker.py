#This file validates user input and returns errors otherwise

import json
import geopandas as gpd

  
###########################################################
def boundary_check(boundary):

  #Only one entry
  if boundary.shape[0] != 1:
    return 'Too many boundaries'

  #Entry is not empty
  if boundary['geometry'][0].is_empty:
    return 'No boundary object provided'

  #Entry is a polygon
  if boundary['geometry'][0].geom_type != 'Polygon':
    return 'Boundary object is not a polygon'

  #Entry is valid
  if boundary['geometry'][0].is_valid == False:
    return 'Boundary object is invalid'

  #Less than Maximum Size (640 acres in m2)
  if boundary['geometry'][0].area > 2589988:
    return 'boundary too large'

  #More than the Minimum Size (5 acres in m2)
  if boundary['geometry'][0].area < 4047:
    return 'Boundary too small'

  #Less than Maximum Length (4 mi in meters)
  if boundary['geometry'][0].length > 6437:
    return 'Boundary too long'

  else:
    return 'OK'


###########################################################
def points_check(points):

  #Only two columns
  if points.shape[1] != 2:
    return 'Invalid number of properties provided'

  #All points aren't null
  if (points['geometry'].is_empty == True).any():
    return 'Not all points have geometries'

  #All geometries are points
  if (points['geometry'].geom_type != 'Point').any():
    return 'Not all geometries are points'

  else:
    return 'OK'

###########################################################
def combined_check(boundary, points):
  
  #All points are within the boundary
  if (points.within(boundary.loc[0, 'geometry']) == False).any():
    return 'Not all points within boundary'

  return 'OK'


###########################################################
def write_out(boundary, points, taskID):

  #Write the files out
  #boundary = boundary.to_crs({'init': 'epsg:4326'})
  boundary.to_file(taskID + '/rootdata/boundary.shp')
  
  #points = points.to_crs({'init': 'epsg:4326'})
  points.to_file(taskID + '/rootdata/points.shp')


###########################################################
def check(inputObject):
  
  #Load data into geodataframes
  boundary = gpd.GeoDataFrame.from_features(inputObject['boundary']['features'])
  boundary.crs = {'init': 'epsg:4326'}
  boundary = boundary.to_crs({'init': 'epsg:26916'})

  points = gpd.GeoDataFrame.from_features(inputObject['points']['features'])
  points.crs = {'init': 'epsg:4326'}
  points = points.to_crs({'init': 'epsg:26916'})
   
  #Run the checks
  response = boundary_check(boundary)
  if response != 'OK':  
    return response

  response = points_check(points)
  if response != 'OK':  
    return response

  response = combined_check(boundary, points)
  if response != 'OK':  
    return response

  #If all's good, write the data out
  write_out(boundary, points, inputObject['id'])

  return 'OK'



 
