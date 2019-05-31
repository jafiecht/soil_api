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
  tif_filename = './../public/' + taskID + '.tif'
  jpg_filename = './../public/' + taskID + '.jpg'

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

  subprocess.call('gdal_translate -of JPEG -scale -q ' + unclipped_filename + ' ' + jpg_filename , shell=True)
 
  #Clip the new raster
  clip(unclipped_filename, tif_filename, taskID)
  return


#Clip to field boundary
def clip(unclipped_filename, tif_filename, taskID):
  
  #If the filename already exists, this will delete it
  if os.path.exists(tif_filename):
    os.remove(tif_filename)

  #Clips the raster to the boundary shapefile.
  command = 'gdalwarp -q -cutline ' + taskID + '/rootdata/boundary.shp -crop_to_cutline ' + unclipped_filename + ' ' + tif_filename
  os.system(command)
  os.system('rm ' + unclipped_filename)
