#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
read_json
Description: Reading json files
Author: Susan Reefman
Date: 17/11/2023

"""

import os, json
import pandas as pd
from datetime import datetime

def read_json(path_to_json):
    
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    
    
    # here I define my pandas Dataframe with the columns I want to get from the json
    jsons_data = pd.DataFrame(columns=['date', 'average', 'doy'])
    
    # we need both the json and an index number so use enumerate()
    for index, js in enumerate(json_files):
        with open(os.path.join(path_to_json, js)) as json_file:
            json_text = json.load(json_file)
    
            # here you need to know the layout of your json and each json has to have
            # the same structure (obviously not the structure I have here)
            average = json_text['average']
            minimum = json_text['minimum']
            maximum = json_text['maximum']

            if 'date' in json_text:
                date = datetime.strptime(json_text['date'], "%Y-%m-%d")
            else:
                x = js.split('_')
                date = datetime.strptime(x[2], "%Y-%m-%d")
            # here I push a list of data into a pandas DataFrame at row given by 'index'
            jsons_data.loc[index] = [date, average, date.timetuple().tm_yday]
    
    return jsons_data
    
