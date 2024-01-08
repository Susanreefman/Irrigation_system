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
    path = 'C:/Users/Susan/Downloads/sample.csv'
    field = 11
    df = pd.read_csv(path)


    # ET0 calculation from weather data
    # weatherdataprocessing.main(weather_df)
    df = ET0calculation.main(df, field)
                
    # Kc curve calculations from NDVI data
   
    # ndviprocessing.main(df, name)
            ## Change ndvi_df to df_processed
    df_Kc = Kc_curve.main(df, field)
            
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
