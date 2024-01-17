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
import logging

logger = logging.getLogger(__name__)

# Constants
ALBEDO = 0.23
A_S = 0.25
B_S = 0.50

# Functions
def calculate_vpd(tmin, tmax, rhmin, rhmax):
    """
    Calculate vapour pressure deficit (VPD) by the actual vapour pressure
    and the mean saturation vapour pressure through temperature and relative
    humidity

    Args:
        tmin (float): daily minimum temperature (°C).
        tmax (float): daily maximum temperature (°C).
        rhmin (float): daily minimum relative humidity (%)
        rhmax (float): daily maximum relative humdity (%)

    Returns:
        e_s (float): mean saturation vapour pressure
        e_a (float): actual vapour pressure
    """
    e0t_min = 0.618 * math.exp((17.27 * tmin) / (tmin + 237.3))
    e0t_max = 0.618 * math.exp((17.27 * tmax) / (tmax + 237.3))

    e_s = (e0t_min + e0t_max) / 2
    e_a = ((e0t_min * rhmax) + (e0t_max * rhmin)) / 200

    return e_s,e_a


def calculate_delta(tmean):
    """
    Calculate vapour pressure from mean temperature

    Args:
        tmean (float): daily mean temperature (°C)

    Returns:
        float: slope of saturation vapour pressure curve (delta) (kPa/°C)
    """
    return (4098 * 0.6108 * math.exp(17.27 * tmean / (tmean + 237.3)) /
            ((tmean + 237.3) ** 2))


def calculate_solar_radiation(lat, doy, sunlight_hour, e_a, tmin, tmax, altitude):
    """
    Calculate solar radiation, through geographical information, number of
    direct sunlight hours, temperature and actual vapour pressure.

    Args:
        lat (float): latitude coordinates of location
        doy (float): day in the year
        sunlight_hour (float): number of direct sunlight hours per day
        e_a (float): actual vapour pressure (kPa)
        tmin (float): daily minimum temperature (°C).
        tmax (float): daily maximum temperature (°C).
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

    r_a = (24 * 60 / math.pi * 0.082 * d_r *
          (sunset_hour_angle * math.sin(latitude) * math.sin(solar_declination) +
           math.cos(latitude) * math.cos(solar_declination) * math.sin(sunset_hour_angle)))

    sunshine_duration = (24*sunset_hour_angle) / math.pi
    r_s = (A_S + ((B_S*sunlight_hour)/sunshine_duration))*r_a
    r_s0 = (0.75 + (2e-5)*altitude)*r_a

    r_ns = (1-ALBEDO)*r_s

    r_nl = (4.903e-09 * (((tmin + 273.16) ** 4 + (tmax + 273) ** 4) / 2) *
           (0.34 - (0.14 * (e_a ** 0.5))) * (1.35 * r_s / r_s0 - 0.35))

    return r_ns-r_nl


def penman_monteith(temp, delta, wind_speed, solar_radiation, gamma, e_a, e_s):
    """
    Calculate reference evapotranspiration (ET0) using the Penman-Monteith equation.

    Args:
        T (float): daily mean temperature (°C)
        delta (float): slope of saturation vapour pressure curve (kPa/°C)
        wind_speed (float): Wind speed at 2 meters above ground (m/s-1).
        Rn (float): Solar radiation (MJ/m^2/day).
        air_pressure (float): Air pressure (kPa).
        gamma (float): Psychrometric constant (kPa/°C).
        e_a (float): actual vapour pressure (kPa)
        e_s (float): mean saturation vapour pressure (kPa)

    Returns:
        float: reference evapotranspiration (ET0) in mm/day.
    """
    return ((0.408 * delta * solar_radiation) +
            (gamma * (900/(temp + 273))*wind_speed*(e_s-e_a))) / \
            (delta + gamma*(1 + (0.34 * wind_speed)))




def main(df, logger):
    """
    Main function of this script, calculating reference evapotranspiration
    of each date in pandas dataframe

    Args:
        df(pandas.Dataframe): dataframe with meteorological information

    Returns:
        df(pandas.Dataframe): dataframe with meterological information and ET0
    """

    logger.info("ET0 calculation started. \n")

    for index, row in df.iterrows():
        lat = row['lat']
        tmin = row['Tmin']
        tmax = row['Tmax']
        tmean = row['Tmean']
        rhmin = row['RHmin']
        rhmax = row['RHmax']
        uz = row['uz']
        sunlight_hour = row['n']
        pressure = row['pressure']
        doy = row['doy']
        altitude = row['z']

        # Calculate delta
        delta = calculate_delta(tmean)

        # Calculate gamma
        gamma = 0.000665*pressure

        # Calculate vapour pressure deficit
        e_s, e_a = calculate_vpd(tmin, tmax, rhmin, rhmax)

        # Calculate solar radiation
        solar_radiation = calculate_solar_radiation(lat, doy, sunlight_hour, e_a, tmin, tmax, altitude)

        # Use all parameters in penman monteith method to calculate ET0
        ET0 = penman_monteith(tmean, delta, uz, solar_radiation, gamma, e_a, e_s)

        # Add ET0 to dataframe
        df.at[index, 'ET0'] = round(ET0,1)
  
    logger.info("ET0 calculation completed. \n")

    return df


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
