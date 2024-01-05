#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETcCalculation
Description: calculation of ETc
Author: Susan Reefman
Date: 03/01/2023
Version:1
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

def main(data, name):
    """ """
    
    data['ETc'] = data['ET0'] * data['Kc']
    
    data.to_csv('~/Downloads/Test/data_'+ name + '.csv', index=False)
    
    plt.figure()
    plt.plot(data['doy'], data['ETc'])
    plt.ylabel('ETc')
    plt.xlabel('doy')
    plt.title(name)
    plt.savefig('C:/Users/Susan/Downloads/Test/ETc_' + name + '.png')
    plt.close()
    
    return 0


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by the user.")
        sys.exit(1)


