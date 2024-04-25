#!/usr/bin/env python3
# https://stackoverflow.com/questions/3748136/how-is-cpu-usage-calculated

import os
import json
import numpy as np
import sys

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

# load all the data in 1 dictionary
path = f"./data_1000/docker_stats.json"
all_data = {}
f = open(path, 'r')
data = json.load(f)
f.close()

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
    'websites': list(data['control'].keys())
}

for extn in extn_lst:
    data_dict[extn] = [] # data_dict = {'websites': [list_of_websites], 'extn_lst[i]': [list of [ram_usage]]}

faulty_sites = {}
# faulty_extn = {}
for extn in extn_lst:
    faulty_sites[extn] = []

def check_for_keys(): # key_lst -> list of keys in a website json object, lst -> (extn_lst + data/website)
    global faulty_sites
    global data_dict

    for extn in extn_lst[1:]:
        faulty_urls = list(set(list(data[extn].keys())) - set(list(data['control'].keys())))
        for site in faulty_urls:
            del data[extn][site]

# populate the faulty_sites dict
check_for_keys()

faulty_num = {}
for extn in extn_lst[1:]:
    faulty_num[extn] = 0

for site in data_dict['websites']:
    for extn in extn_lst:
        try:
            if data[extn][site][-1] == '0B':
                data_dict[extn].append(data[extn][site][:-1])
            else:
                data_dict[extn].append(data[extn][site])
        except KeyError as k:
            print(k)
            print(site, extn, "- dropping website")
            faulty_num[extn] += 1
            data_dict[extn].append(data['control'][site])
            continue

print(faulty_num) # manually removed the 0.0 extries corresponding to the number here

max_plot = {}
avg_plot = {}

for extn in extn_lst:
    max_plot[extn] = []
    avg_plot[extn] = []

# custom_control_max = {}
# custom_control_avg = {}

for extn in extn_lst:
    for i in range(len(data_dict['control'])):
        try:
            #max
            max_plot[extn].append(max(data_dict[extn][i]))  

            #avg
            avg_plot[extn].append(sum(data_dict[extn][i]) / len(data_dict[extn][i]))

            # #max
            # custom_control_max[extn].append(max(data_dict['control'][i]))  

            # #avg
            # custom_control_avg[extn].append(sum(data_dict['control'][i]) / len(data_dict['control'][i]))
        except Exception as e:
            print(e)
            continue

avg_np = {}
max_np = {}
for extn in extn_lst:
    avg_np[extn] = np.array(avg_plot[extn]) # 0 - usr, 1 - sys
    max_np[extn] = np.array(max_plot[extn]) # 0 - usr, 1 - sys

ret_data = {}
ram_max = {}
ram_avg = {}

for extn in extn_lst[1:]:
    ram_max[extn] = np.sort(np.array(max_plot[extn]) - np.array(max_plot['control']))
    ram_avg[extn] = np.sort(np.array(avg_plot[extn]) - np.array(avg_plot['control']))


ret_data['ram_max'] = ram_max
ret_data['ram_avg'] = ram_avg

with open('plot_ram.json', 'w') as f:
    json.dump(ret_data, f, cls=NpEncoder)