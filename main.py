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
    """
    ##
    """
    
    # ET0
    path_weather = 'C:/Users/Susan/Documents/Datasets/Zambia/'
    
    files = os.listdir(path_weather)

    for file in files:
        name = file.split('.')[0]
        df = pd.read_csv(path_weather+file)
        df = weatherdataprocessing.main(df)
        df_ET0 = ET0calculation.main(df, name)
    
    # NDVI 
    ## Change to database connection. NEEDED 'date' & 'average' based on date range and location   
    # path_ndvi = 'C:/Users/Susan/Documents/Datasets/Zambia/'
    # file_ndvi = 'data-1703829387865'
    
    path = 'C:/Users/Susan/Downloads/Zambia/ZambiaNDVI'
    files = [f for f in os.listdir(path)]
    for file in files:
        name = file.split('.')[0]
        df = read_json.read_csv(os.path.join(path, file))
        df_processed = ndviprocessing.main(df, name)
        df_Kc = Kc_curve.main(df_processed, name)

    # ETc
    ## Match correct dfs
    # ETcCalculation.main(df1, df2)
     


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
