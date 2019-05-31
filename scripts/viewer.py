#this file imports a tif, then shows it.
import gdal
import matplotlib.pyplot as plt
from matplotlib import cm



#Load .tif file
def show_tif(filename):
  raster = gdal.Open(filename)
  band = raster.GetRasterBand(1).ReadAsArray()
  plt.imshow(band, cmap = cm.Greys)
  plt.colorbar()
  plt.title(filename)
  plt.show()
  raster = None
  return

#show_tif('rfprediction.tif')
