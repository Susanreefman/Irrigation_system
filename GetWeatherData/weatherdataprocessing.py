#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weatherdataprocessing
Description: functions to process weather data.
Author: Susan Reefman
Date: 30/10/2023
"""

import sys
import pandas as pd


def validate_instance_type(data):
    """Validate data """
    flag = True
    colnames = ["lat", "lon", "dt", "sunrise", "sunset", "temp", "pressure", "humidity", "dew_point", "wind_speed"]
    try:
        for i in colnames:
            data[i] = pd.to_numeric(data[i], errors='raise')
        
    except ValueError:
        for i in colnames:
            data[i] = pd.to_numeric(data[i], errors='coerce')
        data = data.dropna()
        flag = False
    
    if flag == True:
        return 'Instance types validated, no instances removed'
    else:
        return 'Rows of the columns where instances are not numeric are deleted'


def data_validation(data):
    """Validate data """
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
    
    return result


def main(file):
    
    print(f'Weather data {file}')
    weatherdata = pd.read_csv(file)    

    data = pd.DataFrame({
        "lat": weatherdata['lat'],
        "lon": weatherdata['lon'],
        "dt": weatherdata['dt'],
        "sunrise": weatherdata['sunrise'],
        "sunset": weatherdata['sunset'],
        "temp": weatherdata['temp'],
        "pressure": weatherdata['pressure'],
        "humidity": weatherdata['humidity'],
        "dew_point": weatherdata['dew_point'],
        "wind_speed": weatherdata['wind_speed'],
        "weather": weatherdata['weather_main']
    })
    
    data.columns = ["lat", "lon", "dt", "sunrise", "sunset", "temp", "pressure", "humidity", "dew_point", "wind_speed", "weather"]
    
    # Validation of type of instances
    result_type = validate_instance_type(data)
    print(result_type)
    
    # Convert date column
    data['date_per_hour'] = pd.to_datetime(data['dt'], origin='1970-01-01', unit='s', utc=True)
    data['date'] = pd.to_datetime(data['date_per_hour'].dt.strftime('%Y-%m-%d'))
    
    # Validation of dataset contents
    result = data_validation(data)
    print(result)
    
    # Convert sunrise and sunset to human readable datetime
    data['sunrise'] = pd.to_datetime(data['sunrise'], origin='1970-01-01', unit='s', utc=True)
    data['sunset'] = pd.to_datetime(data['sunset'], origin='1970-01-01', unit='s', utc=True)
     
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
    df['day_of_year'] = df['date'].apply(lambda x: x.timetuple().tm_yday)
    
    print("Dataset Processed")
    
    return df


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)


