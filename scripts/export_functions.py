#Imports
###########################################################
import gdal
import numpy as np
import os
import subprocess
import viewer

#Script Body
###########################################################

#Transform prediction list into output tif
def output_tif(predictions, shape, geotrans, proj, taskID):
  prediction_list = predictions
  prediction_array = list()

  unclipped_filename = taskID + '/unclipped.tif'
  tif_filename = './public/' + taskID + '.tif'
  jpg_filename = './public/' + taskID + '.jpg'

  #Reshape the predictions into the output array
  for i in range(shape[0]):
    prediction_array.append(prediction_list[0:(shape[1])])

    for j in range(shape[1]):
      if len(prediction_list) > 0:
        prediction_list.pop(0)
  
  #Write data out as tif
  band = np.array(prediction_array)
  x_pixels = shape[1]
  y_pixels = shape[0]
  driver = gdal.GetDriverByName('GTiff')
  dataset = driver.Create(unclipped_filename, x_pixels, y_pixels, 1, gdal.GDT_Float32)
  dataset.GetRasterBand(1).WriteArray(band)
  dataset.SetGeoTransform(geotrans)
  dataset.SetProjection(proj)
  dataset.FlushCache()
  dataset = None
 
  if os.path.exists(jpg_filename):
    os.remove(jpg_filename)

  #Get the bounds of the unclipped raster
  bounds = GetCornerCoordinates(unclipped_filename)

  subprocess.call('gdal_translate -of JPEG -scale -q ' + unclipped_filename + ' ' + jpg_filename , shell=True)

 
  #Clip the new raster
  clip(unclipped_filename, tif_filename, taskID)
  return bounds


#Clip to field boundary
###########################################################
def clip(unclipped_filename, tif_filename, taskID):
  
  #If the filename already exists, this will delete it
  if os.path.exists(tif_filename):
    os.remove(tif_filename)

  #Clips the raster to the boundary shapefile.
  command = 'gdalwarp -q -cutline ' + taskID + '/rootdata/boundary.shp -crop_to_cutline ' + unclipped_filename + ' ' + tif_filename
  os.system(command)
  os.system('rm ' + unclipped_filename)


#Get the bounds of the unclipped raster
###########################################################
def GetCornerCoordinates(FileName):
  GdalInfo = subprocess.check_output('gdalinfo ' + FileName, shell=True)
  GdalInfo = GdalInfo.decode('utf-8').split('\n') # Creates a line by line list.
  CornerLats, CornerLons = [], []
  GotUL, GotUR, GotLL, GotLR, GotC = False, False, False, False, False
  for line in GdalInfo:
    if line[:10] == 'Upper Left':
        lat, lon = GetLatLon(line)
        CornerLats.append(lat)
        CornerLons.append(lon)
        GotUL = True
    if line[:10] == 'Lower Left':
        lat, lon = GetLatLon(line)
        CornerLats.append(lat)
        CornerLons.append(lon)
        GotLL = True
    if line[:11] == 'Upper Right':
        lat, lon = GetLatLon(line)
        CornerLats.append(lat)
        CornerLons.append(lon)
        GotUR = True
    if line[:11] == 'Lower Right':
        lat, lon = GetLatLon(line)
        CornerLats.append(lat)
        CornerLons.append(lon)
        GotLR = True
    if line[:6] == 'Center':
        lat, lon = GetLatLon(line)
        CornerLats.append(lat)
        CornerLons.append(lon)
        GotC = True 
    if GotUL and GotUR and GotLL and GotLR and GotC:
      break
  bounds = [[], []]
  bounds[0].append(min(CornerLats))
  bounds[1].append(max(CornerLats))
  bounds[0].append(min(CornerLons))
  bounds[1].append(max(CornerLons))
  return bounds 

def GetLatLon(line):
  coords = line.split(') (')[0]
  coords = coords.split('( ')[1]
  LonStr, LatStr = coords.split(', ')
  return float(LatStr), float(LonStr)



