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
import argparse
import pandas as pd
import math
 
# Constants
# lat = 33.409193
# lng = -112.677836
albedo = 0.23
a_s = 0.25
b_s = 0.50

# Crocetta
# altitude = 240

# Guibergia
altitude = 238

# Sabena
# altitude = 238

# Azienda
# altitude = 278

# Cascina
# altitude = 301

# Martello
# altitude = 323




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
    

def Rn(lat, doy, n, ea, T_min, T_max):
    latitude = lat*math.pi/180
    
    d_r = 1 + 0.033 * math.cos(2 * math.pi * doy / 365)
    solar_declination = 0.409 * math.sin(2 * math.pi * doy / 365 - 1.39)
    sunset_hour_angle = math.acos(-math.tan(latitude) * math.tan(solar_declination))
    Ra = 24 * 60 / math.pi * 0.082 * d_r * (sunset_hour_angle * math.sin(latitude) * math.sin(solar_declination) + math.cos(latitude) * math.cos(solar_declination) * math.sin(sunset_hour_angle))
    
    N = (24*sunset_hour_angle) / math.pi 
    Rs = (a_s + ((b_s*n)/N))*Ra
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
    return ((0.408 * delta * Rn) + (gamma * (900/(T + 273))*wind_speed*(es-ea))) / (delta + gamma*(1 + (0.34 * wind_speed)))

    


def main(df):
    """
    
    """
    print("ET calculation started")
    
    ETo = dict()
    newdict = dict()
    wind=[] 
    date, temp, vapour, wind_speed, solar, P, psy, esea = [], [], [], [], [], [], [], []
    
    for index, row in df.iterrows():
        row = row.to_list()
        
        date = row[0]
        lat = row[1]
        lon = row[2]
        Tmin = row[3]
        Tmax = row[4]
        Tmean = row[5]
        RHmin = row[6]
        RHmax = row[7]
        uz = row[8]
        n = row[9]
        pressure = row[10]
        doy = row[11]
        
        delta = calculate_delta(Tmean)
        
        gamma = 0.000665*pressure 
        
        vpd = calculate_VPD(Tmin, Tmax, RHmin, RHmax)
        es = vpd[0]
        ea = vpd[1]
        
        solar_radiation = Rn(lat, doy, n, ea, Tmin, Tmax)
        
    
        ET0 = penman_monteith(Tmean, delta, uz, solar_radiation, pressure, gamma, ea, es)
        
        ETo[date] = round(ET0,1)
        
        df.at[index, 'ET'] = round(ET0,1)
        df.at[index, 'solar'] = solar_radiation
        
        # Convert date keys to datetime objects for sorting
        date_objects = [date for date in ETo.keys()]
    
        # Create a list of sorted date-value pairs
        sorted_date_value_pairs = sorted(zip(date_objects, ETo.values()))
    
        # Create a new dictionary with sorted date keys
        sorted_date_dict = {date.strftime('%d/%m/%Y'): round(value,6) for date, value in sorted_date_value_pairs}
    
    result_file = '~/Downloads/result.csv'
    df.to_csv(result_file, index=False)
    
    print(f'Results saved in "{result_file}"')
    # print(sorted_date_dict)

    # print(ETo.values())
        


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
