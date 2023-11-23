# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:12:29 2023

@author: Susan
"""

import pwlf
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import pandas as pd
import statsmodels.api as sm
from plotnine import ggplot, aes, geom_point
from scipy.optimize import curve_fit
from sklearn import linear_model
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from scipy.interpolate import interp1d



# Define the function for the linear equation Kc = a * average + b
def linear_equation(average, a, b):
    return a * average + b

def pwlf_function(x, y):
    # initialize piecewise linear fit with your x and y data
    my_pwlf = pwlf.PiecewiseLinFit(x, y)
        
    # fit the data for four line segments
    my_pwlf.fit(5)
        
    # predict for the determined points
    xHat = np.linspace(min(x), max(x), num=100)
    yHat = my_pwlf.predict(xHat)
    xHat = [round(value) for value in xHat]
    breakpoints = my_pwlf.fit_breaks
    
    return xHat, yHat, breakpoints.tolist()

# Function to level certain parts of the curve
def level_curve(k):
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
    
    # Generate a range of days from the minimum to the maximum
    df = pd.DataFrame(list(k.items()), columns=['doy', 'Kc'])
    full_range = pd.DataFrame({'doy': range(df['doy'].min(), df['doy'].max() + 1)})
    
    # Merge to include all days in the range
    merged = pd.merge(df, full_range, on='doy', how='right')
    
    # Interpolate the 'average' column
    merged['Kc'] = merged['Kc'].interpolate()
    
    return merged
    
    
def main():
       
    path = "C:/Users/Susan/Downloads/CleanedNDVI"
    # files = [f for f in os.listdir(path)]
    files = ['cleaned_ndvi_2020fullMartello.csv']#, 'cleaned_ndvi_2021fullGuibergia.csv', 'cleaned_ndvi_2021fullMartello.csv']
    for file in files:
        print(f'field: {file}')
        df = pd.read_csv(os.path.join(path, file))

        # maxavg = int(df['average'].idxmax())
        
        x = np.array(df['doy'])
        y = np.array(df['average'])
        
        xHat, yHat, breakpoints = pwlf_function(x,y)
        breakpoints = [round(point) for point in breakpoints]

        # Kc = 1.25 * yHat + 0.2

        k = {}
        for i in breakpoints:
            k[int(round(i))] = 1.25 * df.loc[df['doy'] == int(round(i)), 'average'].values[0] + 0.2
            
        # devstage = df[(df['doy'] >= round(breakpoints[1])) & (df['doy'] <= round(breakpoints[2]))]
        # devstage= devstage.reset_index() 
        # devstage = devstage.drop('index', axis=1)
        # devstage = devstage.drop('normal_avg', axis=1)
        # print(devstage.head())

        print(k)
        k = level_curve(k)
        k = interpolate(k)
        print(k['Kc'].to_string())
        print(k['doy'])
        
        # plot the results
        plt.figure()
        plt.plot(x, y, '-', linewidth=0.5)
        plt.plot(xHat, yHat, ':', linewidth=1.5)
        plt.yticks([0,0.2,0.4,0.6,0.8,1,1.2])
        plt.xticks(list(range(90, 300, 10)),rotation=45, ha='right')#, ['Apr', 'Jun', 'Jul','Aug','Sep', 'Okt', 'Nov'])
        for point in breakpoints:
            # print(point)
            plt.axvline(point, color='lightgray', linestyle='--', label='Breakpoint')   
        plt.grid()
        plt.ylabel('NDVI')
        plt.xlabel('doy')
        plt.title(file)  
        
        
        plt.figure()
        plt.plot(k['doy'], k['Kc'])
        plt.yticks([0,0.2,0.4,0.6,0.8,1,1.2])
        # plt.xticks(list(range(round(k['doy'].min() / 10) * 10, k['doy'].max(), 30)),rotation=45, ha='right')
        plt.xticks(list(range(90, 300, 30)), ['Apr', 'Jun', 'Jul','Aug','Sep', 'Okt', 'Nov'], rotation=45, ha='right')
        for point in breakpoints:
            plt.axvline(point, color='lightgray', linestyle='--', label='Breakpoint')
        plt.text(110, 0.1, 'ini', color='darkgray', fontsize=8)
        plt.text(140, 0.1, 'dev', color='darkgray', fontsize=8)
        plt.text(200, 0.1, 'mid', color='darkgray', fontsize=8)
        plt.text(240, 0.1, 'end', color='darkgray', fontsize=8)
        # plt.grid()
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

