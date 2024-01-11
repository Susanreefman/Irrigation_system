#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main
Description: main function to calculate ETc from given input file, writing to given outputfile
Author: Susan Reefman
Date: 30/10/2023
Version: 1.1
"""

# Import necessary modules
import sys
import pandas as pd
import argparse

# Import additional scripts
import ET0calculation
from NDVI_Data import Kc_curve
import ETcCalculation


# Functions
def parse_args():
    """
    parse command-line arguments for input and output files

    Returns:
        parser.parse_args()
    """ 
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",
                        help="""The location and name to meteorological data in CSV format""",
                        required=True)
    parser.add_argument("-r", "--result",
                        help="""The location and name result file in CSV format""",
                        required=True)
    return parser.parse_args()


def read_data(file):
    """
    Read file and create pandas dataframe

    Args:
        file (str): filepath of input file

    Returns:
        df (pandas.Dataframe): dataframe with meteorological information from 
        inputfile
    """ 

    try:
        df = pd.read_csv(file)
            
    except FileNotFoundError:
        print(f"File '{file}' not found.")
    except IOError as e:
        print(f"An error occurred while reading the file: {e}")

    return df


def main():
    """
    Main function from program, calling the scripts ET0calculation.py, 
    Kc_curve.py and ETcCalculation.py
    """
    # Parse and read file to dataframe
    args = parse_args()
    df = read_data(args.file)

    # ET0 calculation from weather data
    df = ET0calculation.main(df)
    
    # Kc curve calculations from NDVI data
    df_Kc = Kc_curve.main(df)
            
    # ETc calculation
    df_ETc = ETcCalculation.main(df_Kc)       
    
    print(df_ETc)
    # Save to CSV file
    # df_ETc.to_csv(args.result, index=False)
    
    return 0
     


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
