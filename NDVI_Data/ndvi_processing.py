#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ndviprocessing
Description: Processing of NDVI values
Author: Susan Reefman
Date: 17/11/2023
Version: 1.1
"""

# Importing
import sys
import argparse
import pandas as pd
import logging
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter 

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
    """
    Create logger to store information with a specified log file

    Returns:
        logger (logging.Logger): The configured logger instance.
    """
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    file_handler = logging.FileHandler('NDVI_processing_log.log')
    file_handler.setLevel(logging.DEBUG)
    
    # Create a formatter and set the formatter for the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

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
        sys.exit(1)
    except IOError as e:
        logger.info(f"An error occurred while reading the file: {e} \n")
        sys.exit(1)

    return df

    
def remove_zeros(df):
    """ 
    Remove all average value below 0.1
    
    Args:
        df (pandas.DataFrame): dataframe with 'doy' and 'average' NDVI values

    Returns:
        cdf (pandas.DataFrame): dataframe with 'doy' and 'average' NDVI values
    """
    cdf = pd.DataFrame(columns=['average', 'doy'])
    for index, row in df.iterrows():
        avg = df['average'][index]
        if avg > 0.1:
            cdf.loc[len(cdf)] = [df['average'][index], df['doy'][index]]
    return cdf


def remove_continuous_drops_left(data, date):
    """ 
    Remove drops in the left side of the NDVI curve
    
    Args:
        data (list): list with average NDVI values
        date (list): list with day in the year values

    Returns:
        corrected_date (list): list with day in the year values
        corrected_data (list): list with average NDVI values
    """
    corrected_data = [data[0]]
    corrected_date = [date[0]] # Start with the first value
    in_drop = False  # Flag to indicate if we're in a continuous drop
    drop_start_value = data[0]  # Value at the start of the last detected drop

    for i in range(1, len(data)):
        if in_drop:
            # If we're in a drop, check if the current value is less than a 20% drop from the start
            if data[i] < (drop_start_value * 0.80):
                corrected_data.append(corrected_data[-1])  # Continue the drop, use the previous corrected value
                corrected_date.append(corrected_date[-1])  # Continue the drop, use the previous corrected value                
            else:
                in_drop = False  # No longer in a drop
                corrected_data.append(data[i])
                corrected_date.append(date[i])
                drop_start_value = data[i]  # Reset the drop start value
        else:
            # Calculate the percentage drop from the last non-drop value
            drop_percentage = (corrected_data[-1] - data[i]) / corrected_data[-1] if corrected_data[-1] != 0 else 0
            # If there is a drop greater than 20%, we enter a drop state
            if drop_percentage > 0.2:
                in_drop = True
                corrected_data.append(corrected_data[-1])  # Replace the drop
                corrected_date.append(corrected_date[-1])
            else:
                corrected_data.append(data[i])
                corrected_date.append(date[i])

    return corrected_date, corrected_data


def remove_continuous_drops_right(data, date):
    """ 
    Remove drops in the right side of the NDVI curve
    
    Args:
        data (list): list with average NDVI values
        date (list): list with day in the year values

    Returns:
        corrected_date (list): list with day in the year values
        corrected_data (list): list with average NDVI values
    """
    corrected_data = [data[0]]
    corrected_date = [date[0]]  # Start with the first value
    in_drop = False  # Flag to indicate if we're in a continuous drop
    drop_end_index = 0  # Index at the end of the last detected drop
    drop_start_value = data[0]  # Value at the start of the last detected drop

    for i in range(1, len(data)):
        if in_drop:
            # If we're in a drop, continue until the drop ends
            if data[i] >= data[i - 1] or data[i] >= (drop_start_value * 0.80):
                in_drop = False  # No longer in a drop
                corrected_data.extend(data[drop_end_index:i])
                corrected_date.extend(date[drop_end_index:i])
        else:
            # Check for a potential drop (if the current value is less than the previous value)
            if data[i] < data[i - 1]:
                in_drop = True
                drop_end_index = i - 1  # Set the drop end index
                drop_start_value = data[i - 1]  # Set the starting value of the drop

    # Add the remaining data points after the last drop (if any)
    if drop_end_index < len(data) - 1:
        corrected_data.extend(data[drop_end_index + 1:])
        corrected_date.extend(date[drop_end_index + 1:])

    return corrected_date, corrected_data


def interpolate(df):
    """ 
    Interpolate datapoints in dataframe for days that are missing in dataframe
    
    Args:
        df (pandas.DataFrame): dataframe with 'doy' and 'average' NDVI values

    Returns:
        merged (pandas.DataFrame): dataframe with interpolated datapoints     
    """
    # Generate a range of days from the minimum to the maximum
    full_range = pd.DataFrame({'doy': range(int(df['doy'].min()), int(df['doy'].max()) + 1)})
    
    # Merge to include all days in the range
    merged = pd.merge(df, full_range, on='doy', how='right')
    
    # Interpolate the 'average' column
    merged['average'] = merged['average'].interpolate()
    
    return merged


    
def main():
    """ 
    Main function of this script processing NDVI data
    """
    
    # Configure logger
    logger = configure_logger()
    
    # Log the start of the main script
    logger.info("NDVI processing started.\n")

    # Parse and read file to dataframe
    args = parse_args()
    logger.info(f"Using input file: {args.file} \n")
    df = read_data(args.file, logger)
    
    logger.info(f'Datapoints in dataset: {len(df["average"])}')
    
    df_filtered = remove_zeros(df)
    
    maxavg = int(df_filtered['average'].idxmax())

    # Cut dataframe to crop growth cycle of 160 days
    start = df_filtered.iloc[maxavg]['doy']-75
    end = df_filtered.iloc[maxavg]['doy']+85

    # If growth cycle goes up to end of the year, cut the dataframe to the end of the year
    if end > 365:
        end = max(df_filtered['doy'])
    
    df = df_filtered[(df_filtered['doy'] >= start) & (df_filtered['doy'] <= end)]
    
    df = df.reset_index()
    df = df.drop('index', axis=1)
    
    # Split dataframe in a left and right side of the curve, with average as breakpoint
    maxavg = int(df['average'].idxmax())
    left = df.iloc[:maxavg+1]
    right = df.iloc[maxavg:]
    
    right = right.reset_index()
    
    # Removing drops from both sides of the curve
    doy_l, datal = remove_continuous_drops_left(left['average'], left['doy'])
    doy_r, datar = remove_continuous_drops_right(right['average'], right['doy'])
    
    # Smooth left and right side curves
    smleft = savgol_filter(datal, window_length=3, polyorder=1)
    smright = savgol_filter(datar, window_length=3, polyorder=1)
    
    # Create new dataframes
    left = pd.DataFrame({'average': smleft, 'doy': doy_l})
    right = pd.DataFrame({'average': smright, 'doy': doy_r})
    
    logger.info(f'After removing drops: left side of curve {left.shape}, right side of curve {right.shape}')
    
    # Interpolate datapoints
    interpolate_left = interpolate(left)
    interpolate_right = interpolate(right)
    
    logger.info(f'After interpolating: left side of curve {interpolate_left.shape}, right side of curve {interpolate_right.shape}')

    # Merge left and right side of curve to new dataframe
    merge = pd.concat([interpolate_left, interpolate_right], axis=0)
    
    logger.info(f'shape of dataframe: {merge.shape} \n')
    
    # Save to file in csv format
    merge.to_csv(args.result, index=False)
    
    logger.info(f'Dataframe saved in: {args.result}')
    
    # Plot figure
    plt.figure()
    plt.plot(df['doy'], df['average'], color='#00FF00', linewidth=0.5)
    plt.plot(merge['doy'], merge['average'])
    plt.ylabel('NDVI')
    plt.xlabel('Day in year')
    plt.title('NDVI')
    plt.yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
    plt.savefig(args.result + '.png')
    
    logger.info(f'Created image saved in: {args.result}.png \n')
    
    logger.info("NDVI processing completed.")
    
    # Close the logger handlers to release resources
    logging.shutdown()
    
    return 0

    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)

