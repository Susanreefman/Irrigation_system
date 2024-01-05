#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
model
Description: algorithm model to predict ETc 
Author: Susan Reefman
Date: 04/01/2023
Version:1
"""

import sys
import xgboost as xgb
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pandas as pd
import matplotlib.pyplot as plt


def xgboost_train(X,y):
    """ """
    # Splitting the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Creating the XGBoost regression model
    xg_reg = xgb.XGBRegressor(objective ='reg:squarederror', seed=42)

    # Training the model
    xg_reg.fit(X_train, y_train)

    # Making predictions on the test set
    y_pred = xg_reg.predict(X_test)

    # Calculating and printing the Mean Squared Error
    mse = mean_squared_error(y_test, y_pred)
    
    ## Add to log file
    print(f"Mean Squared Error: {mse}")
    
    return xg_reg


def xgboost_test(xg_reg, X_new):
    """ """
    predictions = xg_reg.predict(X_new)

    return predictions


def main():

    data = pd.read_csv('C:/Users/Susan/Downloads/data_to_train.csv')
    new_data = pd.read_csv('C:/Users/Susan/Downloads/data_to_predict.csv')

    ## Add info from data to log file
    #print(data.head())
    #print(new_data.head())

    #Split the data into features and target variable
    X = data[['date','field','Tmin','Tmax','Tmean','RHmin','RHmax','uz','n','day_of_year', 'ET0']]
    y = data['ETc']

    xg_reg = xgboost_train(X,y)
    
    # Make predictions
    X_new = new_data[['date', 'field','Tmin','Tmax','Tmean','RHmin','RHmax','uz','n','day_of_year', 'ET0']]
    predictions = xgboost_test(xg_reg, X_new)

    # Add predicted ETc to dataframe
    new_data['ETc'] = predictions

    new_data['date'].dtype
    new_data['datex'] = pd.to_datetime(new_data['date']+86400, origin='1970-01-01', unit='s', utc=False)

    result = new_data.groupby(new_data['field'])    
    for name, group in result:
        plt.figure()
        plt.plot(group['datex'], group['ETc'])
        # plt.yticks([0,0.2,0.4,0.6,0.8,1,1.2])
        plt.ylabel('ETc')
        plt.xlabel('date')
        plt.title(name)
        # plt.savefig('C:/Users/Susan/Downloads/Test/Kc_' + file + '.png')
    
    new_data.to_csv('C:/Users/Susan/Downloads/predictedresults.csv', index=False)

    return 0 


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)

