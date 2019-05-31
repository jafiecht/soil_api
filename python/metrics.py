#This calculates validation metrics

#Imports
import geopandas as gpd
import rasterio
from rasterio import features
import os

#Get pairs of predicted and actual values
def get_pairs(validation, predicted):

  #Open the template raster, read data and change nodata value
  template = rasterio.open(predicted)
  predicted_array = template.read(1)

  #Read the rasterized point data back in as an array
  test = rasterio.open('individuals/' + validation)
  test_array = test.read(1)
  
  #Initialize empty list
  value_pairs = list()

  #If the test value isn't nodata, pull the test value and
  #the predicted value of the same point.
  for i in range(test_array.shape[0]):
    for j in range(test_array.shape[1]):
      if test_array[i, j] < 9999:
        value_pair = [test_array[i,j], predicted_array[i,j]]
        value_pairs.append(value_pair)
  
  #Give the list of y and yhat back
  return value_pairs



#Calculate the R2 metric of the list
def calculate_R2(y, yhat):
  #Average of the true values
  ybar = sum(y)/len(y)
  #Initialize the SST and SSE metrics
  SST = 0
  SSE = 0
  #Execute for every value pair
  n = len(y)
  for i in range(n):
    #Calculate the squared errors for one value pair
    ST = (y[i] - ybar)**2
    SE = (y[i] - yhat[i])**2
    #Add the square error to the sum
    SST = SST + ST
    SSE = SSE + SE
  #Calculate the R2 value
  R2 = 1 - SSE/SST
  return R2


#Calculate the Root Mean Squared Error
def calculate_RMSE(y, yhat):
  #intialize the MSE metric
  MSE = 0
  #Execute for every value pair
  n = len(yhat)
  for i in range(n):
    #Calculate the squared error and add it to the sum
    SE = (yhat[i] - y[i])**2
    MSE = MSE + SE
  #Take the root of the Mean Squared Error
  RMSE = (MSE/n)**(1/2)
  return RMSE


#Calculate the Mean Error
def calculate_ME(y, yhat):
  #intialize the MSE metric
  ME = 0
  #Execute for every value pair
  n = len(yhat)
  for i in range(n):
    #Calculate the error and add it to the sum
    E = (yhat[i] - y[i])
    ME = ME + E
  #Find the mean error
  ME = (ME/n)
  return ME

#Calculate the Mean Average Error
def calculate_MAE(y, yhat):
  #intialize the MSE metric
  MAE = 0
  #Execute for every value pair
  n = len(yhat)
  for i in range(n):
    #Calculate the error and add it to the sum
    E = abs((yhat[i] - y[i]))
    MAE = MAE + E
  #Find the mean error
  MAE = (MAE/n)
  return MAE



#This function returns validatation metrics
def generate_metrics(values): 
  y = [row[0] for row in values]
  yhat = [row[1] for row in values]
  r2 = calculate_R2(y, yhat)
  rmse = calculate_RMSE(y, yhat)
  me = calculate_ME(y, yhat)
  mae = calculate_MAE(y, yhat)
  return [r2, rmse, me, mae]

