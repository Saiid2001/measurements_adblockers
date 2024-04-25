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

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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

def jsStats(webdriver):
    try:
        jsUsed = webdriver.execute_script("return window.performance.memory.usedJSHeapSize")
    except Exception as e:
        print(e)
        return -1
    
    return jsUsed

def main(number_of_tries):
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('website')
    parser.add_argument('--timeout', type=int, default=60)
    parser.add_argument('--extensions')
    parser.add_argument('--extensions-wait', type=int, default=10)
    parser.add_argument('--cpu')
    args = parser.parse_args()
    # Start X
    vdisplay = Display(visible=False, size=(1920, 1080))
    vdisplay.start()
    # Prepare Chrome
    options = Options()
    #options.headless = False
    # options.add_argument("--headless=new")
    options.add_argument("no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36") 
    #options.add_extension("/home/seluser/measure/harexporttrigger-0.6.3.crx")
    options.binary_location = "/usr/bin/google-chrome"
    # Install other addons
    extensions_path = pathlib.Path("/home/seluser/measure/extensions/extn_crx")
    fname = '/jsheap/' + args.website.split('//')[1]
    extn = fname
    if args.extensions != "control":
        for extension in args.extensions.split(","):
            matches = list(extensions_path.glob("{}*.crx".format(extension)))
            if matches and len(matches) == 1:
                options.add_extension(str(matches[0]))
                extn = extension
            else:
                print(f"{args.extensions} - Extension not found")
                sys.exit(1)
    # Launch Chrome and install our extension for getting HARs
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(args.timeout)

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

    stat_data = {}
    try:
        # started = datetime.now()
        driver.get(args.website)

        wait_until_loaded(driver, args.timeout)

        # collect jsStats
        usedHeap  = jsStats(driver)
        stat_data["jsStats"] = usedHeap

    except Exception as e:
        print(e, "SITE: ", args.website)
        if number_of_tries == 0:
            sys.exit(1)
        else:
            driver.quit()
            # vdisplay.stop()
            return main(number_of_tries-1)

    if os.path.isfile(fname):
        f = open(fname, 'r')
        data = json.loads(f.read())
        f.close()
    else:
        # open the /jsheap/website file and create the dict
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

if __name__ == '__main__':
    main(3)
