# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:12:29 2023

@author: Susan
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
    xHat = np.linspace(min(x), max(x), num=100)
    yHat = my_pwlf.predict(xHat)
    xHat = [round(value) for value in xHat]
    breakpoints = my_pwlf.fit_breaks
    
    return xHat, yHat, breakpoints.tolist()

def level_curve(k):
    """ """
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
    """ """
    # Generate a range of days from the minimum to the maximum
    df = pd.DataFrame(list(k.items()), columns=['doy', 'Kc'])
    full_range = pd.DataFrame({'doy': range(df['doy'].min(), df['doy'].max() + 1)})
    
    # Merge to include all days in the range
    merged = pd.merge(df, full_range, on='doy', how='right')
    
    # Interpolate the 'average' column
    merged['Kc'] = merged['Kc'].interpolate()
    
    return merged
    
    
def main():
       
    path = "C:/Users/Susan/Downloads/CleanedNDVI/"
    files = [f for f in os.listdir(path)]

    for file in files:
        print(f'field: {file}')
        df = pd.read_csv(os.path.join(path, file))
        
        x = np.array(df['doy'])
        y = np.array(df['average'])
        
        xHat, yHat, breakpoints = pwlf_function(x,y)
        breakpoints = [round(point) for point in breakpoints]

        k = {}
        for i in breakpoints:
            k[int(round(i))] = 1.25 * df.loc[df['doy'] == int(round(i)), 'average'].values[0] + 0.2
            
        k = level_curve(k)
        merged = interpolate(k)
        
        merged.to_csv('~/Downloads/Kc_'+file, index=False)
        
        # plot the results
        plt.figure()
        plt.plot(x, y, '-', linewidth=0.5)
        plt.plot(xHat, yHat, ':', linewidth=1.5)
        plt.yticks([0,0.2,0.4,0.6,0.8,1,1.2])
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        for point in breakpoints:
            plt.axvline(point, color='lightgray', linestyle='--', label='Breakpoint')
        plt.grid()
        plt.ylabel('NDVI')
        plt.xlabel('doy')
        plt.title(file)  
        
        plt.figure()
        plt.plot(merged['doy'], merged['Kc'])
        
        for kx, ky in zip (k.keys(), k.values()):
            plt.annotate(kx, (kx,ky),textcoords="offset points",xytext=(0,10), ha='center')
        plt.yticks([0,0.2,0.4,0.6,0.8,1,1.2])
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        for point in breakpoints:
            plt.axvline(point, color='lightgray', linestyle='--', label='breakpoint')
        plt.text(120, 0.1, 'ini', color='darkgray', fontsize=8)
        plt.text(150, 0.1, 'dev', color='darkgray', fontsize=8)
        plt.text(200, 0.1, 'mid', color='darkgray', fontsize=8)
        plt.text(250, 0.1, 'end', color='darkgray', fontsize=8)
        plt.ylabel('Kc')
        plt.xlabel('doy')
        plt.title(file)  
        
    return 0


    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)

