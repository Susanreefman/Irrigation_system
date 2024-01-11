#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ET0
Description: Calculation of reference evapotranspiration (ET0) from 
meterological parameters using the Penman-monteith method. 
Author: Susan Reefman
Date: 13/09/2023
Version:1.1
"""

# Import necessary modules
import sys
import math
 
# Constants
albedo = 0.23
a_s = 0.25
b_s = 0.50

# Functions
def calculate_VPD(Tmin, Tmax, RHmin, RHmax):
    """
    Calculate vapour pressure deficit (VPD) by the actual vapour pressure 
    and the mean saturation vapour pressure through temperature and relative
    humidity

    Args:
        Tmin (float): daily minimum temperature (°C).
        Tmax (float): daily maximum temperature (°C).
        RHmin (float): daily minimum relative humidity (%)
        RHmax (float): daily maximum relative humdity (%)

    Returns:
        es (float): mean saturation vapour pressure
        ea (float): actual vapour pressure
    """   
    e0T_min = 0.618 * math.exp((17.27 * Tmin) / (Tmin + 237.3))
    e0T_max = 0.618 * math.exp((17.27 * Tmax) / (Tmax + 237.3))

    es = (e0T_min + e0T_max) / 2
    ea = ((e0T_min * RHmax) + (e0T_max * RHmin)) / 200

    return es,ea
    

def calculate_delta(T_mean):
    """
    Calculate vapour pressure from mean temperature

    Args:
        Tmean (float): daily mean temperature (°C)

    Returns:
        float: slope of saturation vapour pressure curve (delta) (kPa/°C)
    """   
    return (4098 * 0.6108 * math.exp(17.27 * T_mean / (T_mean + 237.3)) /
            ((T_mean + 237.3) ** 2))    


def Rn(lat, doy, n, ea, Tmin, Tmax, altitude):
    """
    Calculate solar radiation, through geographical information, number of 
    direct sunlight hours, temperature and actual vapour pressure. 

    Args:
        lat (float): latitude coordinates of location
        doy (float): day in the year 
        n (float): number of direct sunlight hours per day
        ea (float): actual vapour pressure (kPa)
        Tmin (float): daily minimum temperature (°C).
        Tmax (float): daily maximum temperature (°C).
        altitude (float): altitude of location (m)

    Returns:
        float: solar radiation (MJ/m^2/day)
    """
    # convert latitude to radians
    latitude = lat*math.pi/180
    
    # calculate solar radiation parameters
    d_r = 1 + 0.033 * math.cos(2 * math.pi * doy / 365)
    solar_declination = 0.409 * math.sin(2 * math.pi * doy / 365 - 1.39)
    sunset_hour_angle = math.acos(-math.tan(latitude) * math.tan(solar_declination))
    
    Ra = (24 * 60 / math.pi * 0.082 * d_r *
          (sunset_hour_angle * math.sin(latitude) * math.sin(solar_declination) +
           math.cos(latitude) * math.cos(solar_declination) * math.sin(sunset_hour_angle)))

    N = (24*sunset_hour_angle) / math.pi 
    Rs = (a_s + ((b_s*n)/N))*Ra
    Rs0 = (0.75 + (2e-5)*altitude)*Ra
    
    Rns = (1-albedo)*Rs
    
    Rnl = (4.903e-09 * (((Tmin + 273.16) ** 4 + (Tmax + 273) ** 4) / 2) *
           (0.34 - (0.14 * (ea ** 0.5))) * (1.35 * Rs / Rs0 - 0.35))
    
    return Rns-Rnl    


def penman_monteith(T, delta, wind_speed, Rn, air_pressure, gamma, ea, es):
    """
    Calculate reference evapotranspiration (ET0) using the Penman-Monteith equation.

    Args:
        T (float): daily mean temperature (°C)
        delta (float): slope of saturation vapour pressure curve (kPa/°C)
        wind_speed (float): Wind speed at 2 meters above ground (m/s-1).
        Rn (float): Solar radiation (MJ/m^2/day).
        air_pressure (float): Air pressure (kPa).
        gamma (float): Psychrometric constant (kPa/°C).
        ea (float): actual vapour pressure (kPa)
        es (float): mean saturation vapour pressure (kPa)

    Returns:
        float: reference evapotranspiration (ET0) in mm/day.
    """    
    return ((0.408 * delta * Rn) + (gamma * (900/(T + 273))*wind_speed*(es-ea))) / (delta + gamma*(1 + (0.34 * wind_speed)))

    


def main(df):
    """
    Main function of this script, calculating reference evapotranspiration 
    of each date in pandas dataframe
    
    Args:
        df(pandas.Dataframe): dataframe with meteorological information
        
    Returns:
        df(pandas.Dataframe): dataframe with meterological information and ET0
    """
    
    ## Add to log file
    # print("ET calculation started")
    
    for index, row in df.iterrows():
        lat = row['lat']
        Tmin = row['Tmin']
        Tmax = row['Tmax']
        Tmean = row['Tmean']
        RHmin = row['RHmin']
        RHmax = row['RHmax']
        uz = row['uz']
        n = row['n']
        pressure = row['pressure']
        doy = row['doy']
        altitude = row['z']
        
        # Calculate delta
        delta = calculate_delta(Tmean)
        
        # Calculate gamma
        gamma = 0.000665*pressure 
        
        # Calculate vapour pressure deficit
        es, ea = calculate_VPD(Tmin, Tmax, RHmin, RHmax)
        
        # Calculate solar radiation
        solar_radiation = Rn(lat, doy, n, ea, Tmin, Tmax, altitude)
    
        # Use all parameters in penman monteith method to calculate ET0
        ET0 = penman_monteith(Tmean, delta, uz, solar_radiation, pressure, gamma, ea, es)
               
        # Add ET0 to dataframe
        df.at[index, 'ET0'] = round(ET0,1)

    ## Add to log file 
    #print(f'Results saved in "{result_file}"')
    #print('--------------------------------')
    
    return df


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
