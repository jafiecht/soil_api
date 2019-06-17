import geopandas as gpd
import pandas as pd
import shapely
import json
import matplotlib.pyplot as plt
import requests
import subprocess
import os

def getDEM(taskID):

  #Load boundary, reproject, buffer, then reproject again
  #################################################################
  boundary = gpd.read_file(taskID + '/rootdata/boundary.shp')
  #boundary = boundary.to_crs({'init': 'epsg:26916'})
  buffered = boundary.copy()
  buffered['geometry'] = buffered['geometry'].buffer(125)
  buffered['geometry'] = buffered['geometry'].envelope
  buffered.to_file(taskID + '/rootdata/buffered_boundary.shp')
  buffered = buffered.to_crs({'init': 'epsg:4326'})

  #Import the tile extent file, then convert to a geodataframe
  #################################################################
  extents = pd.read_csv('./scripts/boundaries.csv', sep=",", header=None, names=['path', 'geometry'])
  extents['geometry'] = extents['geometry'].apply(json.loads)
  extents['geometry'] = extents['geometry'].apply(shapely.geometry.Polygon)
  extents = gpd.GeoDataFrame(extents, geometry='geometry') 
  extents.crs = {'init': 'epsg:4326'}
  
  #Find the tiles that intersect the buffered boundary
  #################################################################
  extents['intersects'] = extents['geometry'].intersects(buffered['geometry'][0])
  paths = extents.loc[(extents['intersects']==True)]['path'].tolist()
  if len(paths) == 0:
    return 'No elevation data available for field'
  
  #Read those files in
  #################################################################
  filenames = list()
  for path in paths:
    tile = requests.get(path, allow_redirects=True)
    if tile.status_code != 200:
      return 'Elevation data for field irretrievable'
    filename = path.rsplit('/', 1)[1]
    filenames.append(taskID + '/topo/' + filename)
    outfile = open(taskID + '/topo/' + filename, 'wb')
    outfile.write(tile.content)
    outfile.close()

  #Process the downloaded tiles
  #################################################################
  #Merge the tiles
  command = 'gdal_merge.py -q -o ' + taskID + '/topo/merged.tif -of GTiff'
  for filename in filenames:
    command = command + ' ' + filename
  subprocess.call(command, shell=True)
 
  #Reproject to UTM
  subprocess.call('gdalwarp -q -t_srs EPSG:26916 ' + taskID + '/topo/merged.tif ' + taskID + '/topo/UTM.tif', shell=True)
  
  #Resample to lower resolution
  subprocess.call('gdalwarp -q -tr 3 3 ' + taskID + '/topo/UTM.tif ' + taskID + '/topo/UTMcoarse.tif', shell=True)

  #Convert to WGS84 and remove the merged file
  #subprocess.call('gdalwarp -q -t_srs EPSG:4326 ' + taskID + '/topo/UTMcoarse.tif ' + taskID + '/topo/WGS84.tif', shell=True)

  #Clip the raster to the buffered boundary and remove the unclipped raster and buffer
  subprocess.call('gdalwarp -q -cutline ' + taskID + '/rootdata/buffered_boundary.shp -crop_to_cutline ' + taskID + '/topo/UTMcoarse.tif ' + taskID + '/topo/elev.tif', shell=True)
  #subprocess.call('gdalwarp -q -cutline ' + taskID + '/rootdata/buffered_boundary.shp -crop_to_cutline ' + taskID + '/topo/WGS84.tif ' + taskID + '/topo/elev.tif', shell=True)
  
  return 'OK'  
