#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main
Description: main function
Author: Susan Reefman
Date: 30/10/2023
"""

# Import necessary modules
import sys
import os
from GetWeatherData import weatherdataprocessing
import ETcalculation
import pandas as pd

# Constants

# Functions


def main():
    """
    
    """
    path = 'C:/Users/Susan/Documents/Datasets/Weatherdata/'
    
    files = os.listdir(path)

    for file in files:
        df = weatherdataprocessing.main(path+file)
        ETcalculation.main(df, file)
    
    


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
