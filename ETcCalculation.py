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

def main(df):
    """ """
    
    df['ETc'] = df['ET0'] * df['Kc']
    
    return df


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)


