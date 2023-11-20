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

def main():
       
    path = "C:/Users/Susan/Downloads/CleanedNDVI"
    files = [f for f in os.listdir(path)]
    print(files)
    for file in files:
        print(f'field: {file}')
        df = pd.read_csv(os.path.join(path, file))

        maxavg = int(df['normal_avg'].idxmax())

        start = df.iloc[maxavg]['doy']-80
        end = df.iloc[maxavg]['doy']+50
        
        df = df[(df['doy'] >= start) & (df['doy'] <= end)]

        df['kc'] = 1.25 * df['normal_avg'] + 0.2
        
        x = np.array(df['doy'])
        y = np.array(df['kc'])
        
        # initialize piecewise linear fit with your x and y data
        my_pwlf = pwlf.PiecewiseLinFit(x, y)
        
        # fit the data for four line segments
        my_pwlf.fit(3)
        
        # predict for the determined points
        xHat = np.linspace(min(x), max(x), num=1000)
        yHat = my_pwlf.predict(xHat)
        breakpoints = my_pwlf.fit_breaks

        # plot the results
        plt.figure()
        plt.plot(x, y, '-', linewidth=0.5)
        plt.plot(xHat, yHat, ':', linewidth=1.5)
        plt.yticks([0,0.2,0.4,0.6,0.8,1,1.2])
        plt.xticks(list(range(90, 300, 30)), ['Apr', 'Jun', 'Jul','Aug','Sep', 'Okt', 'Nov'])
        for point in breakpoints:
            plt.axvline(point, color='lightgray', linestyle='--', label='Breakpoint')        
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

