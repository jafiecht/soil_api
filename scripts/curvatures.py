#This is a test file for developing the quadratic surface generator

#Imports
import rasterio
import numpy as np
import shutil
import os
import scipy.linalg

#########################################################################
def generate_curvatures(taskID):

  #The filepaths for the input DEM and output directories
  srcfp = './' + taskID + '/topo/elev.tif'
  outfp = './' + taskID + '/topo/curvatures/'

  #Open the Raster and Extract needed data
  raster = rasterio.open(srcfp)
  elev = raster.read(1)
  meta = raster.meta.copy()
  meta['nodata'] = 0
  resolution = meta['transform'][1]
  
  #Set the neighborhoods to generate for
  neighborhoods = [5, 25, 55]
  
  #For every neighborhood size, loop through and create maps
  for neighborhood in neighborhoods:
    #print(neighborhood)
  
    #Create output filepaths
    slfp = outfp + 'slope' + str(neighborhood) + '.tif'
    prfp = outfp + 'profile' + str(neighborhood) + '.tif'
    plfp = outfp + 'plan' + str(neighborhood) + '.tif'
    #tgfp = outfp + 'tang' + str(neighborhood) + '.tif'
  
    #Call the slope generation function, returns arrays 
    slope, profile, plan = slope_curvature(elev, resolution, neighborhood)
    #slope, profile, plan, tangential = slope_curvature(elev, resolution, neighborhood)
  
    #Write out the arrays as tifs
    slope_out = rasterio.open(slfp, 'w', **meta)
    slope_out.write(slope.astype(np.float32), 1)
    slope_out.close()
  
    profile_out = rasterio.open(prfp, 'w', **meta)
    profile_out.write(profile.astype(np.float32), 1)
    profile_out.close()
  
    plan_out = rasterio.open(plfp, 'w', **meta)
    plan_out.write(plan.astype(np.float32), 1)
    plan_out.close()
  
    #tang_out = rasterio.open(tgfp, 'w', **meta)
    #tang_out.write(tangential.astype(np.float32), 1)
    #tang_out.close()


#########################################################################
#The master function called from outside
def slope_curvature(dem, res, window_size):
 
  #Define X and Y window datasets
  x = np.ones([window_size, window_size])
  for i in range(x.shape[0]):
    x[i:,] = (i+1)*res - res/2
  X = x.flatten() 
 
  y = np.ones([window_size, window_size])
  for j in range(y.shape[1]):
    y[:,j] = (j+1)*res - res/2
  Y = y.flatten() 

  #Define Central x and y coordinates
  center = int((window_size+1)/2)-1
  central_x = x[center, center]
  central_y = y[center, center]
 
  #Define the size of the output slope/curvature arrays.
  output_size = (
    (dem.shape[0] - window_size + 1), 
    (dem.shape[1] - window_size + 1))
   
  #Initialize the output arrays
  dem_slope = np.zeros(dem.shape)
  dem_profile = np.zeros(dem.shape)
  dem_plan = np.zeros(dem.shape)
  dem_tangential = np.zeros(dem.shape)
  
  #This is a sliding window function. It loops over the input dem 
  #in both axes
  i = 0
  j = 0
  for i in range(output_size[0]):
    
    #Calculate the index to write to in the output arrays
    output_i = int(i + ((window_size+1) / 2) - 1)

    for j in range(output_size[1]):
     
      #Calculate the index to write to in the output arrays
      output_j = int(j + ((window_size+1) / 2) - 1)
      
      #Cut the desired window, fit the quadratic to it, then calculate the 
      #derivatives for the window
      window = dem[i:(i + window_size), j:(j + window_size)]
      C = fit(window, X, Y)
      slope, profile, plan = calculate(C, central_x, central_y)
      #slope, profile, plan, tangential = calculate(C, central_x, central_y)
      
      #Write the vales to the output arrays
      dem_slope[output_i, output_j] = slope
      dem_profile[output_i, output_j] = profile
      dem_plan[output_i, output_j] = plan
      #dem_tangential[output_i, output_j] = tangential

  return dem_slope, dem_profile, dem_plan#, dem_tangential 


#########################################################################
#This function shapes the data and fits a OLS quadratic to it 
def fit(z, X, Y):
  
  #format data 
  Z = z.flatten()
  data = np.c_[X, Y, Z]

  #best-fit quadratic curve (second order)
  A = np.c_[np.ones(data.shape[0]), data[:,:2], np.prod(data[:,:2], axis=1), data[:,:2]**2]
  C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])

  #C is a list of the OLS beta coeffients
  return C


#########################################################################
#This function calculates the desired derivatives, 
#given the OLS coeffiecients
def calculate(C, x, y):

  #Calculate Derivatives
  first_x = C[1] + C[3]*y + 2*C[4]*x
  first_y = C[2] + C[3]*y + 2*C[5]*x
  second_x = 2*C[4]
  second_y = 2*C[5]
  second_xy = C[3]

  #Calculate Terrain Indices
  p = (first_x)**2 + (first_y)**2

  #Now use those to calculate these values
  slope = p**0.5

  profile = ((second_x*(first_x**2)) + (2*second_xy*first_x*first_y) + (second_y*(first_y**2))) / (p*((1+p)**(3/2)))

  plan = ((second_x*(first_x**2)) - (2*second_xy*first_x*first_y) + (second_y*(first_y**2))) / (p**(3/2))
  
  #tangential = ((second_x*(first_x**2)) - (2*second_xy*first_x*first_y) + (second_y*(first_y**2))) / (p*((1+p)**(1/2)))

  return slope, profile, plan#, tangential




