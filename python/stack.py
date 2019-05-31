#This file reads all our feature sets and assembles 
#a feature set.

#Imports
import rasterio
import gdal
import numpy as np
import os
import shutil
import subprocess


#This function returns a dict. with point values and location
def return_points(taskID):
  #Get all the files to run
  filenames = os.listdir(taskID + '/individuals')

  #Run for each file
  point_data = {}  
  for filename in filenames:
    #Open the input raster
    raster = rasterio.open(taskID + '/individuals/' + filename)
    array = raster.read(1)

    #Get the index for the min value (the datapoint)
    flat_index = np.argmin(array)
    index = np.unravel_index(flat_index, array.shape)
    
    #Write the data to the dictionary
    key = os.path.splitext(filename)[0]
    point_data[key] = {'index': index, 'value': array[index]}

  return point_data


#This function returns a dict. with buffer arrays
def return_buffers(taskID):
  #Get all the files to run
  filenames = os.listdir(taskID + '/buffers')

  #Run for each file
  buffers = {}  
  for filename in filenames:
    #Open the input raster
    raster = rasterio.open(taskID + '/buffers/' + filename)
    array = raster.read(1)
    
    #Write the data to the dictionary
    key = os.path.splitext(filename)[0]
    buffers[key] = array

  return buffers


def return_topo(taskID):
  
  #Define stack
  arrays = list()
  labels = list()

  #Import Elevation
  ##########################
  elev_raster = rasterio.open(taskID + '/topo/elev.tif')
  elev = elev_raster.read(1)
  arrays.append(elev)
  labels.append('Elevation')

  #Import Multi-Neighborhood curvatures
  ##########################
  curvlist = os.listdir(taskID + '/topo/curvatures')
  for instance in curvlist:
    curve_raster = rasterio.open(taskID + '/topo/curvatures/' + instance)
    curve = curve_raster.read(1)
    arrays.append(curve)
    labels.append(os.path.splitext(instance)[0])

  return arrays #, labels


def template(feature_set, taskID):

  #Get template data
  raster_shape = feature_set[0].shape
  raster = gdal.Open(taskID + '/topo/elev.tif')
  geotrans = raster.GetGeoTransform()
  proj = raster.GetProjection()

  return raster_shape, geotrans, proj

def cleanup(taskID):
  if os.path.isfile(taskID + '/rootdata/boundary.shp'):
    subprocess.call('rm ' + taskID + '/rootdata/boundary.*', shell=True)
  if os.path.isfile(taskID + '/rootdata/buffered_boundary.shp'):
    subprocess.call('rm ' + taskID + '/rootdata/buffered_boundary.*', shell=True)
  #if os.path.isfile(taskID + '/topo/elev.tif'):
    #subprocess.call('rm ' + taskID + '/topo/elev.tif', shell=True)
  #if os.path.isdir(taskID + '/topo/curvatures/'):
    #shutil.rmtree(taskID + '/topo/curvatures')
    #subprocess.call('mkdir ' + taskID + '/topo/curvatures/', shell=True)
  if os.path.isdir(taskID + '/buffers/'):
    shutil.rmtree(taskID + '/buffers/')
    subprocess.call('mkdir ' + taskID + '/buffers/', shell=True)
  if os.path.isdir(taskID + '/individuals/'):
    shutil.rmtree(taskID + '/individuals/')
    subprocess.call('mkdir ' + taskID + '/individuals/', shell=True)


