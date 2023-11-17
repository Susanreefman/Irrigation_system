# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:12:29 2023

@author: Susan
"""

import pwlf
from ndviprocessing import main
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit

def gaussian(x, amplitude, mean, stddev):
    return amplitude * np.exp(-((x - mean) / stddev) ** 2)


df = main()


doy = df['doy']
avg = df['average']
kc = df['kc']

print(df.to_string)


# Fitting the Gaussian curve to the data
initial_guess = [max(avg), np.mean(doy), np.std(doy)]  # Initial guess for curve fitting parameters
params, covariance = curve_fit(gaussian, doy, avg, p0=initial_guess)

new_avg = gaussian(doy, *params)

# Plotting the data and the fitted curve
plt.figure()
plt.scatter(doy, avg, label='Data')
plt.plot(doy, new_avg, color='red', label='Fitted Gaussian Curve')
plt.xlabel('X-axis (Day of Year)')
plt.ylabel('Y-axis (Average Value)')
plt.legend()
plt.title('Fitting Gaussian Curve to Data')
plt.show()

df['kc_new'] = 1.25 * new_avg + 0.2

x = np.array(df['doy'])
y = np.array(df['kc'])

# initialize piecewise linear fit with your x and y data
my_pwlf = pwlf.PiecewiseLinFit(x, y)

# fit the data for four line segments
res = my_pwlf.fit(4)

# predict for the determined points
xHat = np.linspace(min(x), max(x), num=10000)
yHat = my_pwlf.predict(xHat)

# # plot the results
# plt.figure()
# plt.plot(x, y, '-', linewidth=1.5)
# plt.plot(xHat, yHat, ':', linewidth=1.5)
# plt.yticks([0,0.2,0.4,0.6,0.8,1,1.2])
# plt.ylabel('Kc')


# plot the results
plt.figure()
plt.plot(x, y, '-', linewidth=1)
# plt.plot(xHat, yHat, ':', linewidth=1)
plt.yticks([0,0.2,0.4,0.6,0.8,1,1.2])
plt.ylabel('Kc')



y_new = df['kc_new']
pwlfs = pwlf.PiecewiseLinFit(x, y_new)

# fit the data for four line segments
ress = pwlfs.fit(4)

# predict for the determined points
x_Hat = np.linspace(min(x), max(x), num=10000)
y_Hat = pwlfs.predict(x_Hat)

# plot the results

plt.plot(x, y_new, '--', linewidth=1)
plt.plot(x_Hat, y_Hat, '-.', linewidth=1)
plt.yticks([0,0.2,0.4,0.6,0.8,1,1.2])
plt.ylabel('Kc')
plt.xlabel('Day in year')
plt.grid()
plt.show()