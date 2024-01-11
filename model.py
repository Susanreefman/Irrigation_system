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
import os
import xgboost as xgb
import numpy as np 
import pandas as pd
import argparse
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def is_csv_file(filename):
    """
    check if argument files are in CSV format
    
    Args:
        filename (str): path of file 

    Returns:
        file_extension.lower() == '.csv' (bool): boolean to confirm format
    """ 
    _, file_extension = os.path.splitext(filename)
    
    return file_extension.lower() == '.csv'


def parse_args():
    """
    parse command-line arguments for input and output files
    
    Returns:
        parser.parse_args()
    """ 
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--train",
                        help="""The path and filename of input data 
                        to train model in CSV format""",
                        required=True)
    parser.add_argument("-p", "--predict",
                        help="""The path and filename of input data 
                        to predict in CSV format""",
                        required=True)
    parser.add_argument("-r", "--result",
                        help="""The path and filename of result file 
                        in CSV format""",
                        required=True)
    
    args = parser.parse_args()
    
    if not is_csv_file(args.train) or not is_csv_file(args.predict):
        print("Error: One or more input files are not in CSV format.")
        sys.exit(1) 
    
    return args


def xgboost_train(X,y):
    """
    Training XGBoost algorithm
    
    Args:
        X (pandas.Dataframe): dataframe with information regarding evapotranspiration
        y (pandas.series): series with evapotranspiration values
        
    Returns:
        xg_reg (XGBRegressor): XGBRegressor of the xgboost.sklearn method 
        trained with evapotranspiration information
    """
    # Splitting the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Creating the XGBoost regression model
    xg_reg = xgb.XGBRegressor(objective ='reg:squarederror', seed=42)

    # Training the model
    xg_reg.fit(X_train, y_train)

    # Making predictions on the test set
    y_pred = xg_reg.predict(X_test)

    # Calculating and printing the Mean Squared Error
    rmse = np.sqrt(mean_squared_error(y_test, y_pred)) 

    ## Add to log file
    #print(f"Mean Squared Error: {rmse}")
    
    return xg_reg


def xgboost_test(xg_reg, X_new):
    """
    Testing XGBoost algorithm, predicting ETc
    
    Args:
        xg_reg (XGBRegressor): XGBRegressor of the xgboost.sklearn method 
        trained with evapotranspiration information
        X_new (pandas.Dataframe): dataframe with information regarding evapotranspiration
        
    Returns:
        predictions (np.array): array with ETc predictions
    """
    predictions = xg_reg.predict(X_new)

    return predictions


def main():
    """
    Main function of this script
    """
    args = parse_args()

    data = pd.read_csv(args.train)
    new_data = pd.read_csv(args.predict)

    ## Add info from data to log file

    # Split the data into features and target variable
    X = data[['date','field','Tmin','Tmax','Tmean','RHmin','RHmax','uz','n','day_of_year', 'ET0']]
    y = data['ETc']
    
    # Train XGBoost algorithm on data
    xg_reg = xgboost_train(X,y)
    
    # Make ETc predictions on new data
    X_new = new_data[['date', 'field','Tmin','Tmax','Tmean','RHmin','RHmax','uz','n','day_of_year', 'ET0']]
    predictions = xgboost_test(xg_reg, X_new)
    print(type(predictions))

    # Add predicted ETc to dataframe
    new_data['ETc'] = predictions

    new_data['date'].dtype
    new_data['datex'] = pd.to_datetime(new_data['date']+86400, origin='1970-01-01', unit='s', utc=False)

    # Save data to csv file    
    new_data.to_csv(args.result, index=False)

    return 0 


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)

