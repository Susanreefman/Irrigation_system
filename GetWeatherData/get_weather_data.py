#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
get_weater_data
Description: Get weather data from Open Weather API
Author: Susan Reefman
Date: 23/09/2023


TO DO: add API for altitude
"""

import requests
import csv
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()


configure()

# Get api key from config file 
api_key = os.getenv('api_key')

# Start date in unix timestamp
date = 1627358400

#1april 2021= 1617228000
	

# 1-1-2022
# date = 

flat_data_list = []

for i in range(800):

    api_url = f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat=44.6406&lon=7.6075&dt={date}&units=metric&appid={api_key}'
    date += 3600
    response = requests.get(api_url)

    if response.status_code == 200:
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
            'weather_icon': data['data'][0]['weather'][0]['icon']
        }
        
        flat_data_list.append(flat_data)
      
    else:
        print(f"Error: {response.status_code}")
        
response.close()

# Define path of output CSV file 
csv_file = 'C:/Users/Susan/Documents/Datasets/weather_data_Guibergia2021_aug.csv' 

# Write the data in the list to the CSV file
with open(csv_file, 'w', newline='') as file:
    fieldnames = flat_data.keys()
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(flat_data_list)


