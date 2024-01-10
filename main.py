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
import ET0calculation
from NDVI_Data import Kc_curve
import ETcCalculation
import pandas as pd



def main():
    """ """
    
    ## Change to database connection per location and date range
    path = 'C:/Users/Susan/Downloads/sample.csv'
    field = '11'
    df = pd.read_csv(path)

    # ET0 calculation from weather data
    df = ET0calculation.main(df)
    
    # Kc curve calculations from NDVI data
    df_Kc = Kc_curve.main(df)
            
    # ETc calculation
    df_ETc = ETcCalculation.main(df_Kc)       

    result_file = '~/Downloads/sampleresult_' + field + '.csv'
    df_ETc.to_csv(result_file, index=False)
    
    return 0
     


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
