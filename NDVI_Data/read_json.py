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
    '''Reading JSON file, returning as Dataframe'''
    
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

    jsons_data = pd.DataFrame(columns=['date', 'average', 'doy'])
    
    for index, js in enumerate(json_files):
        with open(os.path.join(path_to_json, js)) as json_file:
            json_text = json.load(json_file)
            average = json_text['average']
            minimum = json_text['minimum']
            maximum = json_text['maximum']

            if 'date' in json_text:
                date = datetime.strptime(json_text['date'], "%Y-%m-%d")
            else:
                x = js.split('_')
                date = datetime.strptime(x[2], "%Y-%m-%d")

            jsons_data.loc[index] = [date, average, date.timetuple().tm_yday]
    
    return jsons_data
    

def read_csv(path_to_csv):
    '''Reading CSV file, returning as dataframe'''
    
    df = pd.read_csv(path_to_csv, usecols=['date', 'average'])
    df['date'] = pd.to_datetime(df['date'],format='%d/%m/%Y')
    df['doy'] = df['date'].apply(lambda x: x.timetuple().tm_yday)
    df = df.reset_index()
    df = df.drop('index', axis=1)
    
    return df
    