#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main
Description: main function
Author: Susan Reefman
Date: 30/10/2023
Version: 1.1
"""

# Import necessary modules
import sys
import os
from GetWeatherData import weatherdataprocessing
import ET0calculation
from NDVI_Data import read_json
from NDVI_Data import ndviprocessing
from NDVI_Data import Kc_curve
import ETcCalculation

import pandas as pd


# Constants

# Functions

def main():
    
    ## Change to database connection per location and date range
    path_weather = 'C:/Users/Susan/Downloads/Weatherdatafields/'
    path_ndvi = 'C:/Users/Susan/Downloads/NDVIfields/'

    weather_files = os.listdir(path_weather)
    ndvi_files = os.listdir(path_ndvi)

    # ET0 calculation from weather data
    for weather_file in weather_files:
        weather_name = weather_file.split('.')[0]
        weather_df = pd.read_csv(os.path.join(path_weather, weather_file))
        weather_df = weatherdataprocessing.main(weather_df)
        df_ET0 = ET0calculation.main(weather_df, weather_name)
        
        # Match NDVI data for the same field
        matching_ndvi = [ndvi_file for ndvi_file in ndvi_files if ndvi_file.split('.')[0] == weather_name]
        
        # Kc curve calculations from NDVI data
        if matching_ndvi:
            ndvi_file = matching_ndvi[0]
            ndvi_name = ndvi_file.split('.')[0]
            ndvi_df = pd.read_csv(os.path.join(path_ndvi, ndvi_file), usecols=['average', 'doy'])
            # df_processed = ndviprocessing.main(df, name)
            ## Change ndvi_df to df_processed
            df_Kc = Kc_curve.main(ndvi_df, ndvi_name)
            
            # Merge data based on day_of_year and doy
            data = pd.merge(df_ET0, df_Kc, left_on='day_of_year', right_on='doy', suffixes=('_ET0', '_Kc'))
            
            #ETc calculation
            ETcCalculation.main(data, ndvi_name)        
    
    return 0
     


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
