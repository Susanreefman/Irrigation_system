#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ET0
Description: Calculation of ET0
Author: Susan Reefman
Date: 13/09/2023
"""

# Import necessary modules
import sys
import pandas as pd
import math
import datasets
import datetime 


# Constants
lat = 33.409193

lng = -112.677836

albedo = 0.23
a_s = 0.25
b_s = 0.50
altitude = 301



# Functions
def read_data(file_path):
    "Read file and create dataframe"

    try:
        df = pd.read_csv(file_path, encoding='cp1252')
            
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IOError as e:
        print(f"An error occurred while reading the file: {e}")


    grouped = df.groupby(df['date'])

    return grouped
    

def get_Tmin(df):
    """ """
    df = df.reset_index()
    return df.loc[0, 'TMin']

def get_Tmax(df):
    """ """
    df = df.reset_index()
    return df.loc[0, 'TMax'] 

def get_RHmin(df):
    """ """
    df = df.reset_index()
    return df.loc[0, 'RHMin']

def get_RHmax(df):
    """ """
    df = df.reset_index()
    return df.loc[0, 'RHMax']

def get_mean_temp(df):
    """ """
    df = df.reset_index()
    return df.loc[0, 'TMean']

def get_day(df):
    """ """
    df = df.reset_index()
    return df.loc[0, 'Day'] 

def get_solar(df):
    """ """
    df = df.reset_index()
    return df.loc[0, 'Solar'] 

def get_mean_windspeed(df, wind):
    """ """
    df = df.reset_index()
    wind.append(df.loc[0, 'WindSpeedMean'])
    return df.loc[0, 'WindSpeedMean']


def calculate_VPD(Tmin, Tmax, RHmin, RHmax):
    """ """
    e0T_min = 0.618 * math.exp((17.27 * Tmin) / (Tmin + 237.3))
    e0T_max = 0.618 * math.exp((17.27 * Tmax) / (Tmax + 237.3))

    es = (e0T_min + e0T_max) / 2
    
    ea = ((e0T_min * RHmax) + (e0T_max * RHmin)) / 200
    
    return [es,ea]
    

def calculate_delta(T_mean):
    """Get vapour pressure from temperature """
    return 4098 * 0.6108 * math.exp(17.27 * T_mean / (T_mean + 237.3)) / ((T_mean + 237.3) ** 2)


def get_atmospheric_pressure(altitude):
    """Get atmospheric pressure from altitude"""
    try:
        df = pd.read_csv(r"..\..\Datasets\P.csv", delimiter=',')

    except FileNotFoundError:
        print(f"File P.csv not found.")
    except IOError as error:
        print(f"An error occurred while reading the file: {error}")

    alt = round(altitude / 50) * 50

    return (df.loc[df['z (m)'] == alt, 'P (kPa)'].values[0])

def get_n(month):
    reference = [8.6,9.2,10.5,11.6,12.5,13.0,12.8,12.0,11.1,10.0,9.1,	8.4]
    return reference[month]
    

def Rn(day, month, ea, T_min, T_max, Rs):
    latitude = lat*math.pi/180
    
    d_r = 1 + 0.033 * math.cos(2 * math.pi * day / 365)
    solar_declination = 0.409 * math.sin(2 * math.pi * day / 365 - 1.39)
    sunset_hour_angle = math.acos(-math.tan(latitude) * math.tan(solar_declination))
    Ra = 24 * 60 / math.pi * 0.082 * d_r * (sunset_hour_angle * math.sin(latitude) * math.sin(solar_declination) + math.cos(latitude) * math.cos(solar_declination) * math.sin(sunset_hour_angle))
    
    
    n = get_n(month)
    N = (24*sunset_hour_angle) / math.pi 
    #Rs = (a_s + ((b_s*n)/N))*Ra
    Rs0 = (0.75 + (2e-5)*altitude)*Ra
    
    Rns = (1-albedo)*Rs
    Rnl = 4.903e-09 * (((T_min+273.16)**4+(T_max + 273)**4)/2) * (0.34 - (0.14 * (ea ** 0.5))) * (1.35 * Rs / Rs0 - 0.35)
    
    return Rns-Rnl    

def penman_monteith(T, delta, wind_speed, Rn, air_pressure, gamma, ea, es):
    """
    Calculate potential evapotranspiration (PET) using the Penman-Monteith equation.

    Args:
        Tmean (float): Tmean in degrees Celsius.
        wind_speed (float): Wind speed at 2 meters above ground in meters per second.
        solar_radiation (float): Solar radiation in MJ/m^2/day.
        air_pressure (float): Air pressure in kPa.
        gamma (float): Psychrometric constant in kPa/°C.

    Returns:
        float: Potential evapotranspiration (PET) in mm/day.
    """    
    return ((0.408 * delta * Rn) + (gamma * (900/(T + 273))*wind_speed*(es-ea))) / (delta + gamma*(1 + (0.34 * wind_speed**2)))

    


def main():
    """
    
    """

    file_path = "../reference.csv"

    
    df = read_data(file_path)
    wind = []
    ETo = dict()
    newdict = dict()
   
    
    date, temp, vapour, wind_speed, solar, P, psy, esea = [], [], [], [], [], [], [], []

    for category, group in df:
        date_obj = datetime.datetime.strptime(category, "%d/%m/%Y")
        month = int(date_obj.strftime("%m"))
        
        day = int(date_obj.strftime("%d"))
        
        Tmin = get_Tmin(group)
        Tmax = get_Tmax(group) 
        Tmean = get_mean_temp(group) #((Tmax+Tmin)/2)
        mean_windspeed = get_mean_windspeed(group, wind)
        
        #Rs
        Rs = get_solar(group)
        
        #delta
        delta = calculate_delta(Tmean)
        
        RHmin = get_RHmin(group)
        RHmax = get_RHmax(group)
        day_year = int(date_obj.strftime('%j'))
        pressure = int(get_atmospheric_pressure(altitude))
        gamma = 0.000665*pressure 
        
        vpd = calculate_VPD(Tmin, Tmax, RHmin, RHmax)
        es = vpd[0]
        ea = vpd[1]
        
        solar_radiation = Rn(day_year, month, ea, Tmin, Tmax, Rs)
        
    
        ET0 = penman_monteith(Tmean, delta, mean_windspeed, solar_radiation, pressure, gamma, ea, es)
        
        ETo[category] = round(ET0,1)
          
        
        # Convert date keys to datetime objects for sorting
        date_objects = [datetime.datetime.strptime(date, '%d/%m/%Y') for date in ETo.keys()]
    
        # Create a list of sorted date-value pairs
        sorted_date_value_pairs = sorted(zip(date_objects, ETo.values()))
    
        # Create a new dictionary with sorted date keys
        sorted_date_dict = {date.strftime('%d/%m/%Y'): round(value,6) for date, value in sorted_date_value_pairs}
    

    print(sorted_date_dict.values())

    # print(ETo.values())
        


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
