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
import argparse
import pandas as pd
import logging

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


def configure_logger():
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    file_handler = logging.FileHandler('main_log.log')
    file_handler.setLevel(logging.DEBUG)
    
    # Check if handlers already exist to avoid duplication
    if not logger.handlers:
        # Create a file handler
        file_handler = logging.FileHandler('main_log.log')
        file_handler.setLevel(logging.DEBUG)

        # Create a formatter and set the formatter for the handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(file_handler)
    else:
        # If the logger is already configured, get the existing logger
        logger = logging.getLogger(__name__)
    logger.propagate = False

    return logger


def read_data(file, logger):
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
        logger.info(f"File '{file}' not found. \n")
    except IOError as e:
        logger.info(f"An error occurred while reading the file: {e} \n")

    return df


def main():
    """
    Main function from program, calling the scripts ET0calculation.py,
    Kc_curve.py and ETcCalculation.py
    """
    
    # Configure logger
    logger = configure_logger()
    
    # Log the start of the main script
    logger.info("Main script started.\n")

    # Parse and read file to dataframe
    args = parse_args()
    logger.info(f"Using input file: {args.file} \n")
    df = read_data(args.file, logger)

    # ET0 calculation from weather data
    df = ET0calculation.main(df.copy(), logger)

    # Kc curve calculations from NDVI data
    df_Kc = Kc_curve.main(df.copy(), logger)

    # ETc calculation
    df_ETc = ETcCalculation.main(df_Kc.copy(), logger)

    # Save to CSV file
    df_ETc.to_csv(args.result, index=False)
    logger.info(f"Result saved in {args.result} \n" )
    
    # Log the end of the main script
    logger.info("Main script finished.")
    
    # Close the logger handlers to release resources
    logging.shutdown()

    return 0



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
