#This file rasterizes .shp point data

import geopandas as gpd
import rasterio
from rasterio import features
import numpy as np

def rasterize(taskID):

  #Filepaths
  infp = taskID + '/rootdata/points.shp'
  templatefp = taskID + '/topo/elev.tif'
  outfp = taskID + '/individuals/'

  #Make a geodataframe, then create an ID column
  points = gpd.read_file(infp)
  points['Point_ID'] = points.index

  #Open the template raster for template information
  template = rasterio.open(templatefp)
  meta = template.meta.copy()
  meta['nodata'] = 9999
  
  #Create an individual file for each point. Useful for buffer creation.
  for index, row in points.iterrows():
    
    #Create a new raster for writing.
    with rasterio.open(outfp+str(row.Point_ID)+'.tif', 'w', **meta) as out:
      out_arr = out.read(1)
     
      #Transform and rasterize shape data
      shapes = ((geom, value) for geom, value in zip([row.geometry], [row[points.columns[0]]]))
      burned = features.rasterize(shapes = shapes, fill=0, out=out_arr, transform=out.transform)
      
      #Write the data out as a raster
      out.write_band(1, burned)
      out.close()
 
