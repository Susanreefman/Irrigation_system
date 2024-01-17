#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
get_weater_data
Description: Get meteorological data from Open Weather API for given date
latitude, longitude per hour. Get altitude through the Google Maps Elevation API
Author: Susan Reefman
Date: 23/09/2023
Version: 2
"""

import os
import sys
import csv
import argparse
import datetime
import requests
from dotenv import load_dotenv


def is_valid_date(date):
    """
    Check if input date given through the commandline is a valid date
    in Unix timestamp

    Args:
        date (int): date in Unix timestamp

    Returns:
        boolean: True when input is valid, False when input is not valid
    """
    try:
        # Attempt to parse the input as a Unix timestamp
        datetime.datetime.utcfromtimestamp(date)
        return True
    except ValueError:
        return False


def is_valid_latitude(latitude):
    """
    Check if input latitude given through the commandline is a valid latitude
    in decimal degrees

    Args:
        latitude (int): latitude in decimal degrees

    Returns:
        boolean: True when input is valid, False when input is not valid
    """
    try:
        # Attempt to parse the input as a float within valid latitude range
        return -90 <= float(latitude) <= 90
    except ValueError:
        return False


def is_valid_longitude(longitude):
    """
    Check if input longitude given through the commandline is a valid longitude
    in decimal degrees

    Args:
        longitude (int): longitude in decimal degrees

    Returns:
        boolean: True when input is valid, False when input is not valid
    """
    try:
        # Attempt to parse the input as a float within valid longitude range
        return -180 <= float(longitude) <= 180
    except ValueError:
        return False


def configure():
    """
    Load .env file with API key
    """
    load_dotenv()


def parse_args():
    """
    parse command-line arguments for input and output files and check validity

    Returns:
        args.date (int): date in Unix timestamp format
        args.latitude (int): latitude of location in decimal degrees
        args.longitude (int): longitude of location in decimal degrees
        args.result (str): path and file name of result file in CSV format
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", type=int,
                        help="""Date in Unix timestamp format""",
                        required=True)
    parser.add_argument("-l", "--latitude",
                        help="""Latitude in decimal degrees""",
                        required=True)
    parser.add_argument("-o", "--longitude",
                        help="""Longitude in decimal degrees""",
                        required=True)
    parser.add_argument("-r", "--result",
                        help="""path and name to result file in CSV format""",
                        required=True)
    args = parser.parse_args()

    if not is_valid_date(args.date):
        print('Invalid date input. Please provide a valid Unix timestamp.')
        return 0

    if not is_valid_latitude(args.latitude):
        print('Invalid latitude input. Please provide a valid decimal degree value within the range [-90, 90].')
        return 0

    if not is_valid_longitude(args.longitude):
        print('Invalid longitude input. Please provide a valid decimal degree value within the range [-180, 180].')
        return 0

    print('All inputs are valid.')


    return args.date, args.latitude, args.longitude, args.result


def get_altitude(lat, lon, api_key):
    """
    Get the altitude for location through Google Maps Elevation API

    Args:
        lat (int): latitude in decimal degrees
        lon (int): longitude in decimal degrees
        api_key (str): key to API
    Returns:
        altitude (int): altitude of given location
    """
    base_url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lon}&key={api_key}"
    response = requests.get(base_url).json()
    check_error_response(response)

    altitude = response['results'][0]['elevation']
    response.close()

    return altitude


def check_error_response(response):
    """
    Check for error in API response, if error exit script

    Args:
        response (dict): response from API
    """
    # Check if the response contains an error
    if 'error_message' in response:
        print("Error has occurred with the Google Maps API:",
              response['error_message'])
        sys.exit(1)


def main():
    """
    Main function of this script.
    Use OpenWeather API and Google Maps Elevation API to get meteorological data
    """
    # Load env file
    configure()

    # Get api key from config file
    api_key_w = os.getenv('api_key_w')
    api_key_a = os.getenv('api_key_a')

    # Get date, latitude, longitude and result file from commandline arguments
    date, latitude, longitude, result = parse_args()

    # Get altitude
    altitude = get_altitude(latitude, longitude, api_key_a)

    flat_data_list = []

    # 24 calls, getting hourly meteorological data for the given date and location
    for _ in range(24):

        api_url = f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={latitude}&lon={longitude}&dt={date}&units=metric&appid={api_key_w}'
        date += 3600

        response = requests.get(api_url)

        # Check for error in response
        if not response.status_code == 200:
            print(f'Error has occurred with the OpenWeather API: {response.status_code}')
            sys.exit(1)

        data = response.json()
        # Flatten the data
        flat_data = {
            'lat': data['lat'],
            'lon': data['lon'],
            'timezone': data['timezone'],
            'timezone_offset': data['timezone_offset'],
            'dt': data['data'][0]['dt'],
            'sunrise': data['data'][0]['sunrise'],
            'sunset': data['data'][0]['sunset'],
            'temp': data['data'][0]['temp'],
            'feels_like': data['data'][0]['feels_like'],
            'pressure': data['data'][0]['pressure'],
            'humidity': data['data'][0]['humidity'],
            'dew_point': data['data'][0]['dew_point'],
            'clouds': data['data'][0]['clouds'],
            'wind_speed': data['data'][0]['wind_speed'],
            'wind_deg': data['data'][0]['wind_deg'],
            'weather_id': data['data'][0]['weather'][0]['id'],
            'weather_main': data['data'][0]['weather'][0]['main'],
            'weather_description': data['data'][0]['weather'][0]['description'],
            'weather_icon': data['data'][0]['weather'][0]['icon'],
            'altitude':altitude
        }

        flat_data_list.append(flat_data)

    response.close()

    # Write the data in the list to the CSV file
    with open(result, 'w', newline='') as file:
        fieldnames = flat_data.keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_data_list)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)