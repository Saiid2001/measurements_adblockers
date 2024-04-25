#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import time
# import threading
import os
from datetime import datetime

import stats

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

extensions_configurations = [
    # No extensions
   "",
#    # Extensions on their own
    "adblock",
    "decentraleyes",
    "disconnect",
    "ghostery",
    "privacy-badger",
    "ublock",
    "adguard",
    # Combinations
#    "decentraleyes,privacy_badger,ublock_origin"
]

def is_loaded(webdriver):
    return webdriver.execute_script("return document.readyState") == "complete"

def wait_until_loaded(webdriver, timeout=60, period=0.25, min_time=0):
    start_time = time.time()
    mustend = time.time() + timeout
    while time.time() < mustend:
        if is_loaded(webdriver):
            if time.time() - start_time < min_time:
                time.sleep(min_time + start_time - time.time())
            return True
        time.sleep(period)
    return False

def webStats(webdriver):
    try:
        navigationStart = webdriver.execute_script("return window.performance.timing.navigationStart")
        # responseStart = webdriver.execute_script("return window.performance.timing.responseStart")
        domComplete = webdriver.execute_script("return window.performance.timing.domComplete")
        loadEnd = webdriver.execute_script("return window.performance.timing.loadEventEnd")
    except Exception as e:
        print(e)
        return -1, -1
    
    return domComplete - navigationStart, loadEnd - navigationStart

def main(number_of_tries, flag, args_lst):
    
    # Start X
    vdisplay = Display(visible=False, size=(1920, 1080))
    vdisplay.start()

    # Prepare Chrome
    options = Options()
    #options.headless = False
    # options.add_argument("--headless=new")
    options.add_argument("no-sandbox")
    options.add_argument("--disable-animations")
    options.add_argument("--disable-web-animations")
    # options.add_argument("--single-process")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--disable-features=AudioServiceOutOfProcess")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36") 
    #options.add_extension("/home/seluser/measure/harexporttrigger-0.6.3.crx")
    options.binary_location = "/usr/bin/google-chrome"

    if flag == 1:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(args_lst[1])

        try:
            driver.get(args_lst[0])
            wait_until_loaded(driver, args_lst[1])

        except Exception as e:
            print(e, "SITE: ", args_lst[0])
            if number_of_tries == 0:
                sys.exit(1)
            else:
                driver.quit()
                # vdisplay.stop()
                return main(number_of_tries-1, flag, args_lst)

        driver.quit()
        vdisplay.stop()

    else:
        # Install other addons
        extensions_path = pathlib.Path("/home/seluser/measure/extensions/extn_crx")
        print(args_lst)
        fname = '/data/' + args_lst[0].split('//')[1]
        extn = fname
        if args_lst[-1]:
            for extension in args_lst[-1].split(","):
                matches = list(extensions_path.glob("{}*.crx".format(extension)))
                if matches and len(matches) == 1:
                    options.add_extension(str(matches[0]))
                    extn = extension
                else:
                    print(f"{args_lst[-1]} - Extension not found")
                    sys.exit(1)
        # Launch Chrome and install our extension for getting HARs
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(args_lst[1])

        # Start perf timer
        #perf = perfevents.PerfEvents(args.timeout)
        stat = stats.Stats(args_lst[1]+10, fname, args_lst[2])
        # We need to wait for everything to open up properly

        time.sleep(2) # wait for extension to load
        if extn == 'adblock':
            time.sleep(15)
        elif extn == 'ghostery':
            windows = driver.window_handles
            for window in windows:
                try:
                    driver.switch_to.window(window)
                    url_start = driver.current_url[:16]
                    if url_start == 'chrome-extension':
                        element = driver.find_element(By.XPATH, "//ui-button[@type='success']")
                        element.click()
                        time.sleep(2)
                        break
                except Exception as e:
                    continue

        try:
            # Make a page load
            stat.start()
            time.sleep(2) # to record 2 extra mpstat cycle
            # started = datetime.now()
            driver.get(args_lst[0])

            wait_until_loaded(driver, args_lst[1])

            # Stop collecting performance data
            stat_data = stat.stop()

            # collect webstats
            domComplete, loadEnd  = webStats(driver)
            stat_data["webStats"] = [domComplete, loadEnd]

        except Exception as e:
            print(e, "SITE: ", args_lst[0])
            if number_of_tries == 0:
                sys.exit(1)
            else:
                driver.quit()
                # vdisplay.stop()
                return main(number_of_tries-1, flag, args_lst)

        if os.path.isfile(fname):
            f = open(fname, 'r')
            data = json.loads(f.read())
            f.close()
        else:
            # open the /data/website file and create the dict
            data = {}
            data['stats'] = {} 

        print("-"*25)
        print(fname)
        print(extn)
        print("-"*25)

        data['stats'][extn] = stat_data

        f = open(fname, 'w')
        json_obj = json.dumps(data)
        f.write(json_obj)
        f.close()

        driver.quit()
        vdisplay.stop()

        time.sleep(3)

if __name__ == '__main__':
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('website')
    parser.add_argument('--timeout', type=int, default=60)
    # parser.add_argument('--extensions')
    parser.add_argument('--extensions-wait', type=int, default=10)
    parser.add_argument('--cpu')
    args = parser.parse_args()

    args_lst = [args.website, args.timeout, args.cpu]

    # calibrate
    for i in range(3):
        main(3, 1, args_lst)

    for extn in extensions_configurations:
        new_args = args_lst
        new_args.append(extn)
        main(3, 0, new_args)
