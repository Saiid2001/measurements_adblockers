import multiprocessing
from bs4 import BeautifulSoup
import re 
import requests
import time

import json
import sys
import math 
import subprocess
from threading import Timer
import os

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

extn_lst = [
     '', 
     'adblock', 
     'ublock'
     , 'privacy-badger',
        "decentraleyes",
        "disconnect",
        "ghostery"
        ,
        "adguard"
    ]

SIZE = 20 # number of browser windows that will open

def run(sites, extn, return_dict, l):
    fname = sites[0].split("//")[1]

    for i in range(3):
        try:
            cmd = ["python3", "chrome/data.py", "--extension", extn, str(sites)]
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)#, timeout = 180)

        except subprocess.TimeoutExpired as t:
            print(f'Timeout for site: {site} {extn}')
            return
        
        except subprocess.CalledProcessError as e:
            print(f'Error for site: {site} {extn}')
            return

        except Exception as e:
            print(e)
            continue
        
        stdout = process.stdout.decode('utf-8')
        stderr = process.stderr.decode('utf-8')
        print('STDOUT:', stdout) 
        print('STDERR:', stderr)
        with open('log', 'a+') as f:
            f.write(f'STDOUT: {stdout}\n') 
            f.write(f'STDERR: {stderr}\n')
        f.close()

if __name__ == "__main__":
    try:
        with open("../../inner_pages_custom.json", "r") as f:
            updated_dict = json.load(f)
        f.close()

        latest_list = list(updated_dict.keys())
        print(len(latest_list))
        chunks_list = list(divide_chunks(latest_list, SIZE))
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        result_dict = {}
        for extn in extn_lst:       
            return_dict[extn] = manager.dict()
            result_dict[extn] = {}
            for i in range(len(chunks_list)):
                jobs = []
                for key in chunks_list[i]:
                    return_dict[extn][key] = manager.list()
                    result_dict[extn][key] = []
                    p = multiprocessing.Process(target=run, args=(updated_dict[key], extn, return_dict, multiprocessing.Lock(),))
                    jobs.append(p)
                for job in jobs:
                    job.start()
                for job in jobs:
                    job.join()
            
            for site in latest_list:
                print(return_dict[extn][site])
                for val in return_dict[extn][site]:
                    result_dict[extn][site].append(val)

    except KeyboardInterrupt:
        print('Interrupted')

        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)

    except Exception as e:
        print(e)
        print('Interrupted')
