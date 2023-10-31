# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 16:08:21 2023

@author: Susan
"""

import pandas as pd
from datetime import datetime
from pytz import UTC
import sys


def process(weatherdata):
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
    data['date_per_hour'] = pd.to_datetime(data['dt'], origin='1970-01-01', unit='s', utc=True)
    data['date'] = data['date_per_hour'].dt.strftime('%Y-%m-%d')
    
    # data['lat'] = pd.to_numeric(data['lat'])
    # data['lon'] = pd.to_numeric(data['lon'])
    # data['temp'] = pd.to_numeric(data['temp'])
    # data['pressure'] = pd.to_numeric(data['pressure'])
    # data['humidity'] = pd.to_numeric(data['humidity'])
    # data['dew_point'] = pd.to_numeric(data['dew_point'])
    # data['wind_speed'] = pd.to_numeric(data['wind_speed'])
    
    # data = data.dropna()
    
    # if not all(data['temp'] >= -20) and not all(data['temp'] <= 40):
    #     data = data[(data['temp'] >= -20) & (data['temp'] <= 40)]
    
    data['pressure'] = data['pressure'] / 10
    
    # if not all(data['pressure'] >= 85) and not all(data['pressure'] <= 110):
    #     data = data[(data['pressure'] >= 85) & (data['pressure'] <= 110)]
    
    # if not all(data['humidity'] >= 0) and not all(data['humidity'] <= 100):
    #     data = data[(data['humidity'] >= 0) & (data['humidity'] <= 100)]
    
    # if not all(data['dew_point'] >= -33) and not all(data['dew_point'] <= 35):
    #     data = data[(data['dew_point'] >= -33) & (data['dew_point'] <= 35)]
    
    # if not all(data['wind_speed'] >= 0) and not all(data['wind_speed'] <= 115):
    #     data = data[(data['wind_speed'] >= 0) & (data['wind_speed'] <= 115)]
    
    data['sunrise'] = pd.to_datetime(data['sunrise'], origin='1970-01-01', unit='s', utc=True)
    data['sunset'] = pd.to_datetime(data['sunset'], origin='1970-01-01', unit='s', utc=True)
    
    unique_dates = data['date'].unique()
    
    for date in unique_dates:
        filtered_data = data[(data['date'] == date) & (data['date_per_hour'] >= data['sunrise']) & (data['date_per_hour'] <= data['sunset'])]
        clear_count = sum(filtered_data['weather'] == "Clear")
        data.loc[data['date'] == date, "sunshine_hour"] = clear_count
    
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
    
    df = df.reset_index(drop=True)

    # Convert the 'date' column to a datetime object
    df['date'] = pd.to_datetime(df['date'])
    
    # Add a new column 'day_of_year'
    df['day_of_year'] = df['date'].apply(lambda x: x.timetuple().tm_yday)
    
    print("dataset processed")
    
    return df




def main():
    weatherdata = pd.read_csv('~/Downloads/full_weather_dataset.csv')
    df = process(weatherdata)

    return df

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)


