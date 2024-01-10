#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kc_curve
Description: processing Kc curves
Author: Susan Reefman
Date: 17/11/2023
Version:1

"""

import pwlf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import sys
import pandas as pd


def pwlf_function(x, y):
    """ initialize piecewise linear fit with your x and y data"""
    my_pwlf = pwlf.PiecewiseLinFit(x, y)
        
    # fit the data for four line segments
    my_pwlf.fit(5)
        
    # predict for the determined points
    xHat = np.linspace(min(x), max(x), num=150)
    yHat = my_pwlf.predict(xHat)
    xHat = [round(value) for value in xHat]
    breakpoints = my_pwlf.fit_breaks
    
    return xHat, yHat, breakpoints.tolist()

def level_curve(k):
    """ ## """
    values_to_update = list(k.values())
    
    for i in range(0, len(values_to_update), 2):
        value1 = values_to_update[i]
        value2 = values_to_update[i + 1]
    
        average = (value1 + value2) / 2  # Calculate the average of values
        values_to_update[i] = average
        values_to_update[i + 1] = average  # Update both values with the average value
    
    # Update the original dictionary with updated values
    updated_values = list(k.keys())
    for i, key in enumerate(updated_values):
        k[key] = values_to_update[i]
    
    return k 

def interpolate(k):
    """ ## """
    # Generate a range of days from the minimum to the maximum
    df = pd.DataFrame(list(k.items()), columns=['doy', 'Kc'])
    
    full_range = pd.DataFrame({'doy': range(df['doy'].min(), df['doy'].max() + 1)})
    
    # Merge to include all days in the range
    merged = pd.merge(df, full_range, on='doy', how='right')
    
    # Interpolate the 'average' column
    merged['Kc'] = merged['Kc'].interpolate()

    return merged
    
    
def main(df): 
    """ ## """
    
    x = np.array(df['doy'])
    y = np.array(df['NDVI'])
    
    xHat, yHat, breakpoints = pwlf_function(x,y)
    breakpoints = [round(point) for point in breakpoints]

    k = {}
    for i in breakpoints:
        k[int(round(i))] = 1.25 * df.loc[df['doy'] == int(round(i)), 'NDVI'].values[0] + 0.2
    k = level_curve(k)
    merged = interpolate(k)
    
    new_df = pd.merge(df, merged, on='doy', how='right')
    
    return new_df


    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)

