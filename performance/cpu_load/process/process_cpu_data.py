#!/usr/bin/env python3
# https://stackoverflow.com/questions/3748136/how-is-cpu-usage-calculated

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import sys

# def trunc(values, decs=0):
#     return np.trunc(values*10**decs)/(10**decs)

def sort(feature_dict):
    zipped = zip(feature_dict[extn_lst[0]], feature_dict[extn_lst[1]], feature_dict[extn_lst[2]], feature_dict[extn_lst[3]])    
    sorted_zipped = sorted(zipped)
    unzipped = list(zip(*sorted_zipped))
    for i in range(len(extn_lst)):
        feature_dict[extn_lst[i]] = list(unzipped[i])
    return feature_dict

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
        dele[extn] = np.array(stat_plot[1][extn])
        d[extn] = {}

        # filter all -1 values from stat_plot
        dummy = np.array(stat_plot[1]['control'])
        index = np.where(dele[extn] == -1)

        np.delete(dele[extn], index)
        np.delete(dummy, index)

        mask2 = np.abs(dummy) > 30000
        count = np.sum(mask2)
        # print('control', websites[mask].tolist())

        mask1 = np.abs(dele[extn]) > 30000
        count = np.sum(mask1)
        # print(extn, websites[mask].tolist())

        result_array = np.setdiff1d(websites[mask1], websites[mask2])
        print(extn, len(result_array))

        zipped = zip(dele[extn] - dummy, websites)
        sorted_zipped = sorted(zipped)
        unzipped = list(zip(*sorted_zipped))
        x = list(unzipped[1]) # x -> website
        y = list(unzipped[0]) # y -> extn_time - ctrl_time
        
        ret[extn] = np.sort(np.array(y))

        for j in range(len(x)):
            d[extn][x[j]] = y[j]


        # # plot
        # plt.plot(np.sort(np.array(y)), label = extn)
        # plt.axhline(np.median(np.array(y)), linestyle='dashed', color='g')
        # plt.legend()
        # plt.show()
        # # plt.savefig(f'stat_{extn}.png')
    return ret
    # import json
    # with open('website_categorization/site_load_time_custom_1000.json', 'w') as f:
    #     json.dump(d, f, cls=NpEncoder)
    # f.close()

# list of all files in /data folder
path = f"./data_1000/data_custom/"
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
            if f'/data/{website}' not in website_data.keys():
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

faulty_num = {}
for extn in extn_lst[1:]:
    faulty_num[extn] = 0

for website in dir_list:
    # control case
    key = '/data/'+website
    data = all_data[website]

    if website in faulty_sites['control']:
        continue
    for extn in extn_lst[1:]:
        if website in faulty_sites[extn]:
            data["stats"][extn] = {"webStats": [-1, -1]}

    data_dict['websites'].append(website)

    try:
        usr_c = data["stats"][key]['usr']
        sys_c = data["stats"][key]['sys']
        iowait_c = data["stats"][key]['iowait']
        webStats_c = data["stats"][key]['webStats']
        data_dict['control'].append([usr_c, sys_c, iowait_c, webStats_c])
    except KeyError as k:
        # print(website, k, "- dropping website")
        faulty_sites += 1
        data_dict['websites'] = data_dict['websites'][:-1]
        continue

    # extn case
    for extn in extn_lst[1:]:  # opting out the 'control' case
        key = extn
        try:
            usr = data["stats"][key]['usr']
            syst = data["stats"][key]['sys']
            iowait = data["stats"][key]['iowait']
            webStats = data["stats"][key]['webStats']
            data_dict[extn].append([usr, syst, iowait, webStats])
        except KeyError as k:
            usr = usr_c
            syst = sys_c
            iowait = iowait_c
            webStats = webStats_c
            data_dict[extn].append([usr, syst, iowait, webStats])
            faulty_num[extn] += 1
            # print(website, extn,  k)
            pass

print(faulty_num) # manually removed the 0.0 extries corresponding to the number here

# data_dict = {'websites':[], 'k1': [[[v1,v2,v3,ws1], [v4,v5,v6,ws2], [v1,v2,v3,ws3]], [[v1,v2,v3,ws11], [v4,v5,v6,ws21], [v1,v2,v3, ws31]]], 'k2': [[[v1,v2,v3], [v4,v5,v6], [v1,v2,v3]], [[v1,v2,v3], [v4,v5,v6], [v1,v2,v3]]], 'k3': [[[v1,v2,v3], [v4,v5,v6], [v1,v2,v3]], [[v1,v2,v3], [v4,v5,v6], [v1,v2,v3]]]}

max_plot = [{}, {}, {}] # for usr, sys, iowait
avg_plot = [{}, {}, {}]
stat_plot = [{}, {}]

for i in range(4): # initialization
    for extn in data_dict:
        if extn != 'websites':
            if (i == 3):
                stat_plot[0][extn] = []
                stat_plot[1][extn] = []
            else:
                max_plot[i][extn] = []
                avg_plot[i][extn] = []
            
for i in range(len(data_dict['control'])):
    for extn in data_dict:
        for j in range(4):
            if extn != 'websites':
                if (j==3):
                    # # filter out -1 values from stat_plot
                    # if data_dict[extn][i][j][0] == -1 or data_dict[extn][i][j][1] == -1:
                    #     continue

                    stat_plot[0][extn].append(data_dict[extn][i][j][0])
                    stat_plot[1][extn].append(data_dict[extn][i][j][1])
                else:
                    #max
                    max_plot[j][extn].append(max(data_dict[extn][i][j]))  

                    #avg
                    avg_plot[j][extn].append(sum(data_dict[extn][i][j][:-3]) / len(data_dict[extn][i][j][:-3])) # can do [:-1] so that last entry can be ignored (which would mostly be close to 0) bcoz I did run mpstat for 5 extra cycle 


# generate_stats_dict(data_dict)

avg_np = {}
max_np = {}
for extn in extn_lst:
    avg_np[extn] = np.array(avg_plot[0][extn]) # 0 - usr, 1 - sys
    max_np[extn] = np.array(max_plot[0][extn]) # 0 - usr, 1 - sys
    # sys_avg[extn] = np.array(avg_plot[1][extn]) # 0 - usr, 1 - sys
    # sys_max[extn] = np.array(max_plot[1][extn]) # 0 - usr, 1 - sys

def plot_max():
    median_lst = []
    mean_lst = []
    for extn in max_np.keys():
        if extn != 'control':
            median_lst.append(np.median(max_np[extn] - max_np['control']))
            mean_lst.append(np.mean(max_np[extn] - max_np['control']))
    # print('max')
    # print(f'median -> {median_lst}')
    # print(f'mean -> {mean_lst}')
        # plt.plot(np.sort(max_np[extn] - max_np['control']), label = extn)
            # plt.axhline(np.median(max_np[extn] - max_np['control']), linestyle='dashed', color='g')
            # plt.legend()
            # plt.show()
            # plt.savefig(f'max_{extn}.png')

def plot_avg():
    median_lst = []
    mean_lst = []
    for extn in avg_np.keys():
        if extn != 'control':
            median_lst.append(np.median(avg_np[extn] - avg_np['control']))
            mean_lst.append(np.mean(avg_np[extn] - avg_np['control']))
    # print('avg')
    # print(f'median -> {median_lst}')
    # print(f'mean -> {mean_lst}')
            # plt.plot(np.sort(avg_np[extn] - avg_np['control']), label = extn)
            # plt.axhline(np.median(avg_np[extn] - avg_np['control']), linestyle='dashed', color='g')
            # plt.legend()
            # plt.show()
            # plt.savefig(f'avg_{extn}.png')

# plot_max()
# plot_avg()

ret_data = {}
usr_max = {}
usr_avg = {}
sys_max = {}
sys_avg = {}
cpu_avg = {}
load_time = {}

# print(np.max(avg_plot[0]['control']))
# print(np.min(avg_plot[0]['control']))

for extn in extn_lst[1:]:
    usr_max[extn] = np.sort(np.array(max_plot[0][extn]) - np.array(max_plot[0]['control']))
    usr_avg[extn] = np.sort(np.array(avg_plot[0][extn]) - np.array(avg_plot[0]['control']))
    sys_max[extn] = np.sort(np.array(max_plot[1][extn]) - np.array(max_plot[1]['control']))
    sys_avg[extn] = np.sort(np.array(avg_plot[1][extn]) - np.array(avg_plot[1]['control']))
    cpu_avg[extn] = np.sort(np.array(avg_plot[0][extn]) + np.array(avg_plot[1][extn]) - np.array(avg_plot[0]['control']))

ret_data['usr_max'] = usr_max
ret_data['usr_avg'] = usr_avg
ret_data['sys_max'] = sys_max
ret_data['sys_avg'] = sys_avg
ret_data['cpu_avg'] = cpu_avg
ret_data['load_time'] = generate_stats_dict(data_dict)

with open('plot_performance.json', 'w') as f:
    json.dump(ret_data, f, cls=NpEncoder)

# print(ret_data['load_time'])

sys.exit(0)
#######################################
'''
NORMAL CASE
max
median -> [-3.9599999999999937, -1.0, -6.145000000000003, -5.844999999999999, -5.0, -6.3799999999999955, 0.2749999999999986, -4.240000000000002, -10.0, 0.06499999999999773, -4.0]
mean -> [-5.7435064935064934, -1.4001623376623376, -7.6505113636363635, -7.278230519480519, -5.354878246753246, -9.205251623376622, 0.37082792207792237, -5.079512987012988, -10.489050324675324, 0.200852272727273, -5.826225649350649]
avg
median -> [-1.2117777777777778, -2.1710955710955773, -9.032083333333333, -7.900148809523815, -1.9025641025640994, -6.999945887445883, 0.9480555555555554, -11.877188057041, -17.395662878787874, 0.1552777777777763, -3.0629440559440564]
mean -> [-2.5169939029084447, -5.236286475272781, -11.234515205394617, -9.274963251309407, -3.8296496978514347, -9.20287175104206, 1.0936166659340183, -14.207587681437737, -18.891461567753563, 0.31433297381449493, -5.3355359002449045]



[:-3] case
avg
median -> [0.4161507936507931, -2.068875000000002, -9.574499999999999, -8.588441558441556, -2.3978472222222216, -10.289294871794878, 1.2245000000000097, -10.0342803030303, -16.799839285714285, 0.11875000000000036, -6.200166666666657]
mean -> [-0.43207449183127755, -3.5955423206120636, -10.333722354778185, -9.298882065242223, -3.1814447423238446, -10.597886548759487, 1.3191576176133057, -10.71205536331635, -16.67451246390721, 0.2667337251197192, -6.63041014645096]


[:-2] case
avg
median -> [-0.5273809523809536, -2.1175000000000033, -9.546722222222222, -8.662777777777777, -2.4517424242424255, -8.616666666666672, 1.0458259619637325, -11.47919642857143, -18.009111111111118, 0.13383333333332992, -4.401476190476188]
mean -> [-1.3927289011919408, -4.410593648940901, -10.96976607660363, -9.515359274615816, -3.65838470590261, -9.68011731468206, 1.1914573253082907, -12.809246036749187, -18.266971182690675, 0.3224435920865198, -5.553189586564677]



'''
