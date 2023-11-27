#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ndviprocessing
Description: Processing of NDVI values
Author: Susan Reefman
Date: 17/11/2023

"""

# Importing
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import read_json
import os
from scipy.signal import savgol_filter 
from scipy.optimize import curve_fit

    
def remove_zeros(df):
    cdf = pd.DataFrame(columns=['date', 'average', 'doy'])
    for index, row in df.iterrows():
        avg = df['average'][index]
        if avg > 0.1:
            cdf.loc[len(cdf)] = [df['date'][index], df['average'][index], df['doy'][index]]
    return cdf


def remove_continuous_drops_left(data, date):
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
    
    # Generate a range of days from the minimum to the maximum
    full_range = pd.DataFrame({'doy': range(df['doy'].min(), df['doy'].max() + 1)})
    
    # Merge to include all days in the range
    merged = pd.merge(df, full_range, on='doy', how='right')
    
    # Interpolate the 'average' column
    merged['average'] = merged['average'].interpolate()
    
    return merged


def gaussian(x, amplitude, mean, stddev):
    return amplitude * np.exp(-((x - mean) / stddev) ** 2)

# Define an exponential function
def exponential(x, a, b):
    return a * np.exp(b * x)

    
def main():
    
    path =  'D:/Nabu/Crosetto/'
    # directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    # directories.remove('NotUsed')
    directories = ['Crosetto_2019.csv', 'Crosetto_2020.csv', 'Crosetto_2021.csv']

    for dirname in directories:
        print(f'field: {dirname}')
        # dt = read_json.read_json(os.path.join(path, dirname))
        dt = read_json.read_csv(os.path.join(path, dirname))
        print(f'Datapoints in dataset: {len(dt["average"])}')
        
        print(dt.to_string())
        
        df_filtered = remove_zeros(dt)

        maxavg = int(df_filtered['average'].idxmax())

        start = df_filtered.iloc[maxavg]['doy']-75
        end = df_filtered.iloc[maxavg]['doy']+120

        if end > 365:
            end = max(df_filtered['doy'])
        
        df = df_filtered[(df_filtered['doy'] >= start) & (df_filtered['doy'] <= end)]
        
        df = df.reset_index()
        df = df.drop('index', axis=1)
        
        maxavg = int(df['average'].idxmax())
        left = df.iloc[:maxavg+1]
        right = df.iloc[maxavg:]
        
        right = right.reset_index()
        
        # Removing drops
        doy_l, datal = remove_continuous_drops_left(left['average'], left['doy'])
        doy_r, datar = remove_continuous_drops_right(right['average'], right['doy'])
        
        # Smooth left and right side curves
        smleft = savgol_filter(datal, window_length=5, polyorder=1)
        smright = savgol_filter(datar, window_length=5, polyorder=1)
        
        # Create new dataframes
        left = pd.DataFrame({'average': smleft, 'doy': doy_l})
        right = pd.DataFrame({'average': smright, 'doy': doy_r})
        print(f'After removing drops: left side of curve {left.shape}, right side of curve {right.shape}')
        
        # Interpolate datapoints
        interpolate_left = interpolate(left)
        interpolate_right = interpolate(right)
        print(f'After interpolating: left side of curve {interpolate_left.shape}, right side of curve {interpolate_right.shape}')

        # Merge left and right side of curve to new dataframe
        merge = pd.concat([interpolate_left, interpolate_right], axis=0)
        print(f'shape of dataframe: {merge.shape}')
        
        # Plot
        plt.figure()
        plt.plot(df['doy'], df['average'], color='#00FF00', linewidth=0.5)
        plt.plot(merge['doy'], merge['average'])
        plt.ylabel('NDVI')
        plt.xlabel('Day in year')
        plt.legend()
        plt.title('NDVI' + dirname)
        plt.xticks(list(range(90, 300, 30)), ['Apr', 'Jun', 'Jul','Aug','Sep', 'Okt', 'Nov'])
        plt.yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
        
        resultcsv = '~/Downloads/CleanedNDVI/cleaned_ndvi_' + dirname + '.csv'
        merge.to_csv(resultcsv, index=False)
  
    return 0

    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
