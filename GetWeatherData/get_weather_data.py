# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 10:02:40 2023

@author: Susan
"""

import requests
import json
import csv

API = "922c67c6382ed3a9626907e565ce178a"
# lat = 44.8619648
# lon = 7.5110815
# time = 1685578353

#api_url = 'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat=44.8619648&lon=7.5110815&dt=1685578353&units=metric&appid=353cecb69d945dbff2eb39c0bfb41f7c'
#api_url = 'https://api.openweathermap.org/data/3.0/onecall/day_summary?lat=44.8619648&lon=7.5110815&date=2023-06-01&units=metric&appid=353cecb69d945dbff2eb39c0bfb41f7c'

# date = 1640991600
# date = 1644051600
date = 1649844000

# june = []
# json_file_path = 'june_data.json'
flat_data_list = []

for i in range(350):

    api_url = f'https://api.openweathermap.org/data/3.0/onecall/timemachine?lat=44.898137&lon=7.767975&dt={date}&units=metric&appid=353cecb69d945dbff2eb39c0bfb41f7c'
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

# Define the CSV file name
csv_file = 'weather_data.csv'

# Write the data in the list to the CSV file
with open(csv_file, 'w', newline='') as file:
    fieldnames = flat_data.keys()
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(flat_data_list)


