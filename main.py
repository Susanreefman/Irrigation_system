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
import pandas as pd
import subprocess
from GetWeatherData import weatherdataprocessing
import ETcalculation

# Constants

# Functions


def main():
    """
    
    """
    df = weatherdataprocessing.main()
    
    ETcalculation.main(df)
    
    


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
