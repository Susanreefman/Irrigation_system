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

    for i in range(1, len(data)):
        drop_percentage = (data[i - 1] - data[i]) / data[i - 1] if data[i - 1] != 0 else 0
        if drop_percentage > 0.2:
            corrected_data.append(corrected_data[-1])  # Replace the dropped value
            corrected_date.append(corrected_date[-1])
        else:
            corrected_data.append(data[i])
            corrected_date.append(date[i])

    return corrected_date, corrected_data


def interpolate(df):
    
    # Generate a range of days from the minimum to the maximum
    full_range = pd.DataFrame({'doy': range(df['doy'].min(), df['doy'].max() + 1)})
    
    # Merge to include all days in the range
    merged = pd.merge(df, full_range, on='doy', how='right')
    
    # Interpolate the 'average' column
    merged['average'] = merged['average'].interpolate()
    
    return merged

    
def main():
    
    path =  'D:/Nabu'
    # directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    # directories.remove('NotUsed')
    directories = ['2021fullGuibergia']#, '2021fullGuibergia']

    for dirname in directories:
        print(f'field: {dirname}')
        dt = read_json.read_json(os.path.join(path, dirname))
        print(f'Datapoints in dataset: {len(dt["average"])}')
        df = remove_zeros(dt)
        maxavg = df['average'].idxmax()

        left = df.iloc[:maxavg+1]
        right = df.iloc[maxavg:]
        right = right.reset_index()
        
        # Removing drops
        doy_l, datal = remove_continuous_drops_left(left['average'], left['doy'])
        doy_r, datar = remove_continuous_drops_right(right['average'], right['doy'])
        
        # Smooth left and right side curves
        smleft = savgol_filter(datal, window_length=3, polyorder=1)
        smright = savgol_filter(datar, window_length=3, polyorder=1)
        
        # Create new dataframes
        left = pd.DataFrame({'average': smleft, 'doy': doy_l})
        right = pd.DataFrame({'average': smright, 'doy': doy_r})
        print(f'After removing drops: left side of curve {left.shape}, right side of curve {right.shape}')
        
        # Interpolate datapoints
        interpolate_left = interpolate(left)
        interpolate_right = interpolate(right)
        print(f'After interpolating: left side of curve {interpolate_left.shape}, right side of curve {interpolate_right.shape}')

        # Merge left and right side of curve to new dataframe
        merged = pd.concat([interpolate_left, interpolate_right], axis=0)
        print(f'shape of dataframe: {merged.shape}')
        
        # Smooth full curve
        merge = pd.DataFrame({'average': savgol_filter(merged['average'], window_length=10, polyorder=1), 'doy': merged['doy']})
        
        # Plot
        plt.figure()
        plt.plot(df['doy'], df['average'], color='#00FF00', linewidth=0.5)
        plt.plot(merge['doy'], merge['average'])
        plt.ylabel('NDVI')
        plt.xlabel('Day in year')
        plt.legend()
        plt.title('NDVI' + dirname)
        # plt.xticks(list(range(0, len(merge['doy']), 30)))
        plt.yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
        
        # # Kc
        # plt.figure()
        merge['kc'] = 1.25 * merge['average'] + 0.2
        # plt.plot(merge['doy'], merge['kc'])
        # plt.grid()
        # plt.ylabel('Kc')
        # plt.title('Kc' + dirname)
        # # plt.xticks(list(range(0, len(merge['doy']), 30)))
        # plt.yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2])
        
        # plt.show
        resultcsv = '~/Downloads/cleaned_ndvi_' + dirname + '.csv'
        merge.to_csv(resultcsv, index=False)
        
        filtered_df = merge[(merge['doy'] >= 100) & (merge['doy'] <= 300)]

  
    return filtered_df

    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
