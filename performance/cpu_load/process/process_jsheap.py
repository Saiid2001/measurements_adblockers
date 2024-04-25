#!/usr/bin/env python3
# https://stackoverflow.com/questions/3748136/how-is-cpu-usage-calculated

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import sys

# def trunc(values, decs=0):
#     return np.trunc(values*10**decs)/(10**decs)

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def generate_stats_dict(data_dict):
    websites = np.array(data_dict['websites'])
    # extn_stat = []
    dele = {}
    d = {}

    ret = {}
    for extn in extn_lst:
        if extn == 'control':
            continue

        # extn_stat.append(np.array(stat_plot[1][extn]))
        dele[extn] = np.array(stat_plot[extn])
        d[extn] = {}

        # filter all -1 values from stat_plot
        dummy = np.array(stat_plot['control'])
        index = np.where(dele[extn] == -1)

        np.delete(dele[extn], index)
        np.delete(dummy, index)
        zipped = zip(dele[extn] - dummy, websites)
        sorted_zipped = sorted(zipped)
        unzipped = list(zip(*sorted_zipped))
        x = list(unzipped[1]) # x -> website
        y = list(unzipped[0]) # y -> extn_time - ctrl_time
        
        ret[extn] = np.sort(np.array(y))

        for j in range(len(x)):
            d[extn][x[j]] = y[j]

    return ret

# list of all files in /data folder
path = f"./data_1000/jsheap/"
dir_list = os.listdir(path)

# extn_lst = ['control', 'adblock', 'ublock', 'privacy-badger']
extn_lst = [
    'control', 'adblock', 'ublock', 'privacy-badger',
       "decentraleyes",
       "disconnect",
       "ghostery",
       "https",
       "noscript",
       "scriptsafe",
       "canvas-antifp",
       "adguard",
       "user-agent"]

data_dict = {
    'websites': []
}

for extn in extn_lst:
    data_dict[extn] = [] # data_dict = {'websites': [list_of_websites], 'extn_lst[i]': [list of [usr, sys, iowait, stats]]}

faulty_sites = {}
# faulty_extn = {}
for extn in extn_lst:
    faulty_sites[extn] = []

def check_for_keys(website_data, website): 
    # website_data -> data dict of each website, website -> website
    global faulty_sites
    for extn in extn_lst:
        if extn == 'control':
            if f'/jsheap/{website}' not in website_data.keys():
                faulty_sites[extn].append(website)
        else:
            if extn not in website_data.keys():
                faulty_sites[extn].append(website)

# load all the data from the files in 1 dictionary
all_data = {}
for website in dir_list:
    f = open(path+website, 'r')
    data = json.load(f)
    f.close()
    all_data[website] = data

# populate the faulty_sites dict
for website in all_data:
    check_for_keys(all_data[website]['stats'], website)

for website in dir_list:
    # control case
    key = '/jsheap/'+website
    data = all_data[website]

    if website in faulty_sites['control']:
        continue
    for extn in extn_lst[1:]:
        if website in faulty_sites[extn]:
            data["stats"][extn] = {"webStats": [-1, -1]}

    data_dict['websites'].append(website)

    try:
        jsheap_c = data["stats"][key]['jsStats']
        data_dict['control'].append(jsheap_c/1048576)
    except KeyError as k:
        print(website, k, "- dropping website")
        faulty_sites += 1
        data_dict['websites'] = data_dict['websites'][:-1]
        continue

    # extn case
    for extn in extn_lst[1:]:  # opting out the 'control' case
        key = extn
        try:
            jsheap = data["stats"][key]['jsStats']
            data_dict[extn].append(jsheap/1048576)
        except KeyError as k:
            jsheap = jsheap_c
            data_dict[extn].append(jsheap/1048576)
            print(website, extn,  k)
            pass

stat_plot = {}

for extn in data_dict:
    if extn != 'websites':
        stat_plot[extn] = []
            
for i in range(len(data_dict['control'])):
    for extn in data_dict:
        if extn != 'websites':
            stat_plot[extn].append(data_dict[extn][i])

# generate_stats_dict(data_dict)
ret_data = {}
js_size = {}
ret_data['jsheap'] = generate_stats_dict(data_dict)

with open('plot_jsheap.json', 'w') as f:
    json.dump(ret_data, f, cls=NpEncoder)