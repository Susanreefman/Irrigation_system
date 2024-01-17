#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETcCalculation
Description: calculation of ETc
Author: Susan Reefman
Date: 03/01/2023
Version:1.1
"""

import sys
import logging

logger = logging.getLogger(__name__)

def main(df, logger):
    """
    Main function of this script, calculating the actual evapotranspiration (ETc)

    Args:
        df (pandas.Dataframe): dataframe with information to calculate ETc

    Returns:
        df (pandas.Dataframe): dataframe with addition of ETc
    """
    logger.info("ETc calculation started. \n")

    # Calculate ETc and add to dataframe
    df['ETc'] = df['ET0'] * df['Kc']

    logger.info("ETc calculation completed. \n")
    
    return df


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)
        