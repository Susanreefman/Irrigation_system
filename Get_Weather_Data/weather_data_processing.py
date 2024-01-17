#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weatherdataprocessing
Description: functions to process weather data.
Author: Susan Reefman
Date: 30/10/2023
Version: 1.1
"""

import sys
import argparse
import logging
import pandas as pd


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
    file_handler = logging.FileHandler('weather_data_processing_log.log')
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


def validate_instance_type(data):
    """
    Validate instance types in dataset

    Args:
        data (pandas.Dataframe): dataframe with weather data

    Returns:
        data (pandas.Dataframe): dataframe with weather data
        (str): string with information about instances removed
    """
    flag = True
    colnames = ["lat", "lon", "dt", "sunrise", "sunset", "temp", "pressure",
                "humidity", "dew_point", "wind_speed"]
    try:
        for i in colnames:
            data[i] = pd.to_numeric(data[i], errors='raise')

    except ValueError:
        for i in colnames:
            data[i] = pd.to_numeric(data[i], errors='coerce')
        data = data.dropna()
        flag = False

    if flag == True:
        return data, 'Instance types validated, no instances removed'

    return data, 'Rows of the columns where instances are not numeric are deleted'


def data_validation(data):
    """
    Validate instance types in dataset

    Args:
        data (pandas.Dataframe): dataframe with weather data

    Returns:
        result (str): string with information about instances removed
        data (pandas.Dataframe): dataframe with weather data
    """
    result = 'Data validated, no instances removed'
    # Temperature of all instances must be between -20 and 40 degrees
    if not (all(data['temp'] > -90.00) and all(data['temp'] < 50.00)):
        data = data[(data['temp'] > -90.00) & (data['temp'] < 50.00)]
        result = 'Removed instances where temperature was lower then -90 or above 50 degrees'

    # Pressure from hPa to kPa, must be between 85 and 110 kPa
    data['pressure'] = data['pressure'] * 0.1
    if not (all(data['pressure'] > 85.00) and all(data['pressure'] < 110.00)):
        data = data[(data['pressure'] > 85.0) & (data['pressure'] < 110.0)]
        result = 'Removed instances where pressure was lower then 85 or above 110 kPa'

    # Humidity must be between 0 and 100%
    if not (all(data['humidity'] >= 0) and all(data['humidity'] <= 100)):
        data = data[(data['humidity'] >= 0) & (data['humidity'] <= 100)]
        print('Removed instances where humidity was lower then 0% or above 100%')

    # Dew point must be between -33 and 35
    if not (all(data['dew_point'] >= -33) and all(data['dew_point'] <= 35)):
        data = data[(data['dew_point'] >= -33) & (data['dew_point'] <= 35)]
        result = 'Removed instances where dew point was lower then -33 or above 35'

    # Windspeed must be between 0 and 110 m/s
    if not (all(data['wind_speed'] >= 0) and all(data['wind_speed'] <= 115)):
        data = data[(data['wind_speed'] >= 0) & (data['wind_speed'] <= 115)]
        result = 'Removed instances where wind speed was lower then 0 or above 115 m/s'

    return data, result


def main():
    """
    Main function of this script processing weather data to dataframe with only
    validated instances.
    """

    # Configure logger
    logger = configure_logger()

    # Log the start of the main script
    logger.info("Main script started.\n")

    # Parse and read file to dataframe
    args = parse_args()
    logger.info(f"Using input file: {args.file} \n")
    df = read_data(args.file, logger)

    data = pd.DataFrame({
        "lat": df['lat'],
        "lon": df['lon'],
        "dt": df['dt'],
        "sunrise": df['sunrise'],
        "sunset": df['sunset'],
        "temp": df['temp'],
        "pressure": df['pressure'],
        "humidity": df['humidity'],
        "dew_point": df['dew_point'],
        "wind_speed": df['wind_speed'],
        "weather": df['weather_main']
    })

    data.columns = ["lat", "lon", "dt", "sunrise", "sunset", "temp",
                    "pressure", "humidity", "dew_point", "wind_speed", "weather"]

    # Validation of type of instances
    data, result_type = validate_instance_type(data)
    logger.info(f"{result_type}")

    # Convert date column
    data['date_per_hour'] = pd.to_datetime(data['dt'],
                                           origin='1970-01-01',
                                           unit='s',
                                           utc=True)
    data['date'] = pd.to_datetime(data['date_per_hour'].dt.strftime('%Y-%m-%d'))

    # Validation of dataset contents
    data, result = data_validation(data)
    logger.info(f"{result} \n")

    # Convert sunrise and sunset to human readable datetime
    data['sunrise'] = pd.to_datetime(data['sunrise'],
                                     origin='1970-01-01',
                                     unit='s',
                                     utc=True)
    data['sunset'] = pd.to_datetime(data['sunset'],
                                    origin='1970-01-01',
                                    unit='s',
                                    utc=True)

    # Count direct sunshine hours per day
    unique_dates = data['date'].unique()

    for date in unique_dates:
        filtered_data = data[(data['date'] == date) & (data['date_per_hour'] >= data['sunrise']) & (data['date_per_hour'] <= data['sunset'])]
        clear_count = sum(filtered_data['weather'] == "Clear")
        data.loc[data['date'] == date, "sunshine_hour"] = clear_count

    # Create new dataframe
    df = pd.DataFrame({
        "date": data['date'].unique(),
        "lat": data.groupby('date')['lat'].min(),
        "lon": data.groupby('date')['lon'].min(),
        "Tmin": data.groupby('date')['temp'].min(),
        "Tmax" : data.groupby('date')['temp'].max(),
        "Tmean" : data.groupby('date')['temp'].mean(),
        "RHmin" :data.groupby('date')['humidity'].min(),
        "RHmax" : data.groupby('date')['humidity'].max(),
        "uz" : data.groupby('date')['wind_speed'].mean(),
        "n" :data.groupby('date')['sunshine_hour'].min(),
        "pressure" : data.groupby('date')['pressure'].mean()
    })

    # Add a new column 'day_of_year'
    df['doy'] = df['date'].apply(lambda x: x.timetuple().tm_yday)

    # Save to CSV file
    df.to_csv(args.result, index=False)
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
