#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kc_curve
Description: calculating Kc curve through piecewise linear fit method. Finding
breakpoints in NDVI values and converting those values to a Kc value.
Author: Susan Reefman
Date: 17/11/2023
Version:1.1
"""

# Imports
import sys
import pwlf
import numpy as np
import pandas as pd

# Functions
def pwlf_function(doy, ndvi):
    """
    initialize piecewise linear fit to find breakpoints in the curve day in the
    year against NDVI values. Breakpoints are indicating growth stages in the
    crop growth cycle.

    Args:
        doy (np.array): array including day in the year values
        ndvi (np.array): array including NDVI values

    Returns:
        breakpoints (list): list with the breakpoints in the Kc curve
        between the growth stages
    """

    my_pwlf = pwlf.PiecewiseLinFit(doy, ndvi)

    # fit the data for 4 line segments
    my_pwlf.fit(5)

    # find breakpoints in curve
    breakpoints = [round(point) for point in my_pwlf.fit_breaks]

    return breakpoints


def level_curve(curve):
    """
    Level the values between the breakpoints of the curve to get a Kc curve

    Args:
        curve (dict): dictionary with day in the year and Kc value for breakpoints

    Returns:
        curve (dict): dictionary with day in the year and updated Kc value
        for breakpoints
    """
    values_to_update = list(curve.values())

    for i in range(0, len(values_to_update), 2):
        value1 = values_to_update[i]
        value2 = values_to_update[i + 1]

        # Calculate the average of values
        average = (value1 + value2) / 2
        values_to_update[i] = average
        # Update both values with the average value
        values_to_update[i + 1] = average

    # Update the original dictionary with updated values
    updated_values = list(curve.keys())
    for i, key in enumerate(updated_values):
        curve[key] = values_to_update[i]

    return curve


def interpolate(curve):
    """
    augmentation of data points between break points in curve
    through interpolate for days that are not in dataframe

    Args:
        curve (dict): dictionary with day in the year and Kc value for breakpoints

    Returns:
        merged (pandas.Dataframe): dataframe with day in the year and
        belonging Kc value
    """
    # Generate a range of days from the minimum to the maximum
    df = pd.DataFrame(list(curve.items()), columns=['doy', 'Kc'])

    full_range = pd.DataFrame({'doy': range(df['doy'].min(), df['doy'].max() + 1)})

    # Merge to include all days in the range
    merged = pd.merge(df, full_range, on='doy', how='right')

    # Interpolate the 'average' column
    merged['Kc'] = merged['Kc'].interpolate()

    return merged


def main(df):
    """
    Main function of this script, calculating Kc value for each date in
    pandas dataframe

    Args:
        df(pandas.Dataframe): dataframe with meteorological information

    Returns:
        new_df(pandas.Dataframe): dataframe with meterological information,
        ET0 and Kc value.
    """

    doy = np.array(df['doy'])
    ndvi = np.array(df['NDVI'])

    breakpoints = pwlf_function(doy,ndvi)

    # Convert NDVI to Kc value
    curve = {}
    for i in breakpoints:
        curve[int(round(i))] = 1.25 * df.loc[df['doy'] == int(round(i)), 'NDVI'].values[0] + 0.2

    # Level line segments in curve
    curve = level_curve(curve)

    # Interpolate points in line segment
    merged = interpolate(curve)

    # Add Kc values to existing dataframe
    new_df = pd.merge(df, merged, on='doy', how='right')

    return new_df



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
