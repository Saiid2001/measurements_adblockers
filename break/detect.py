#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import sys
import time
import threading
import pathlib
import re
import multiprocessing
import os

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from webdriver_manager.core.utils import read_version_from_cmd 
from webdriver_manager.core.os_manager import PATTERN
from webdriver_manager.chrome import ChromeDriverManager

# def check_for_extn_installation(driver, name):  #generates a screenshot to check for extension installation
#     driver.get("https://chrome.google.com/webstore/detail/adblock-plus-free-ad-bloc/cfhdojbkjhnklbpkdaibdccddilifddb")
#     #save screenshot
#     S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
#     driver.set_window_size(S('Width'),S('Height')) # May need manual adjustment
#     file_name = name + '.png'
#     driver.find_element(by=By.TAG_NAME, value='body').screenshot(file_name)

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

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

# Function to print context around match
def print_match_context(match, source):
    start, end = match.start(), match.end()
    # Calculate the start and end positions for the context, ensuring they are within bounds
    context_start = max(start - 40, 0)
    context_end = min(end + 40, len(source))
    # Print the context
    return f"Context: '{source[context_start:context_end]}'"

def check_for_keywords(text):
    # Define the patterns
    allow_pattern = r"allow.{0,5}\s(ad)"
    adblock_pattern = r"adblocker|ad blocker|ad-blocker|adblock\.detect"

    # Search for matches in the source text and print context
    found1 = re.search(allow_pattern, text, re.IGNORECASE)
    found2 = re.search(adblock_pattern, text, re.IGNORECASE)

    if found1:
        # print("Match found for allow pattern:")
        string = print_match_context(found1, text)
        print(string)
        return True
    elif found2:
        # print("Match found for ad blocker pattern:")
        string = print_match_context(found2, text)
        print(string)
        return True
    else:
        # print("No match found.")
        return False

def find_all_iframes(driver):
    iframes = driver.find_elements(By.XPATH, value=".//iframe | .//frame")
    # i = 0
    for iframe in iframes:
        try:
            driver.switch_to.frame(iframe)  
            time.sleep(2)
            text = driver.page_source
            text = text.lower()

            if check_for_keywords(text):
                print(f'adblock keyword detected for: {driver.current_url}')
                return 1
            driver.switch_to.default_content()
        except Exception as e:
            print(e, iframe, "looping through iframes")
    return 0

def detect(driver):
    text = driver.page_source
    text = text.lower()
    if check_for_keywords(text):
        print(f'adblock keyword detected for: {driver.current_url}')
        return 1
    
    time.sleep(2)
    return find_all_iframes(driver)

def initialize_driver(extn, num_tries):
    while num_tries > 0:
        try:
            options = Options()
            extensions_path = pathlib.Path("../extensions/")
            options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            options.binary_location = "../chrome_120/chrome"
            # service = Service(executable_path='/home/ritik/work/pes/chromedriver_113/chromedriver')
            # version = '113.0.5672.0'
            version = '120.0.6099.10900'
            service = Service(ChromeDriverManager(version).install())

            matches = list(extensions_path.glob("{}*.crx".format(extn)))
            if matches and len(matches) == 1:
                options.add_extension(str(matches[0]))

            driver = webdriver.Chrome(options=options, service=service)
            driver.set_page_load_timeout(120)

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
                        print('ghostery', 1, e)
                        return 0
            else:
                time.sleep(5)

            break
        except Exception as e:
            print(e)
            if num_tries == 1:
                print(f"couldn't create browser session... not trying again")
                print(2, e, driver.current_url)
                return 0
            else:
                print("couldn't create browser session... trying again")
                num_tries = num_tries - 1
                time.sleep(5)
        
    return driver

def run(site_lst, extn, key, return_dict, lock, display):
    # display number
    os.environ['DISPLAY'] = f":{display}"

    driver = initialize_driver(extn, 3)

    for site in site_lst:
        try:
            num_tries = 3
            ret_val = 0

            while num_tries > 0:
                driver.get(site)

                try:
                    filepath = f'./page_ss/{extn}'
                    if not os.path.isdir(filepath):
                        os.makedirs(filepath, exist_ok=True)
                    if driver != None:
                        driver.save_screenshot(f'{filepath}/{key}.png')

                except Exception as e:
                    print('Cannot take a screenshot')
                
                wait_until_loaded(driver)
                time.sleep(3)

                # ret_val = find_all_iframes(driver)
                ret_val = detect(driver)
                num_tries -= 1

                if ret_val:
                    break

            if ret_val:
                f = open("blocking_urls.txt", "a+")
                f.write(driver.current_url)
                f.write('\n')
                f.close()

                return_dict[extn].append(key)
                break
        except Exception as e:
            print(e, key)

    driver.quit()

if __name__ == "__main__":
    extn_lst = ['adblock', 'control', 'ublock', 'privacy-badger',
           "decentraleyes",
           "disconnect",
           "ghostery",
           "adguard"]

    with open("../inner_pages_custom.json", "r") as f:
        updated_dict = json.load(f)
    f.close()

    SIZE = 3 # number of browser windows that will open

    latest_list = list(updated_dict.keys())
    # latest_list = ['geeksforgeeks.org', 'reuters.com', 'forbes.com']

    chunks_list = list(divide_chunks(latest_list, SIZE))
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    result_dict = {}
    lock = multiprocessing.Lock()

    xvfb_args = [
        '-maxclients', '1024'
    ]
    vdisplay = Display(backend='xvfb', size=(1920, 1280), extra_args=xvfb_args)
    # vdisplay = Xvfb(width=1920, height=1280)
    vdisplay.start()
    display = vdisplay.display

    for extn in extn_lst:       
        return_dict[extn] = manager.list()
        result_dict[extn] = []
            
        try:
            for i in range(len(chunks_list)):
                jobs = []
                for key in chunks_list[i]:
                    p = multiprocessing.Process(target=run, args=(updated_dict[key], extn, key, return_dict, lock, display, ))
                    jobs.append(p)
                for job in jobs:
                    job.start()

                TIMEOUT = 180
                start = time.time()
                for job in jobs:
                    print(f"joining {job}")
                    job.join(timeout = 60)

                    while time.time() - start <= TIMEOUT:
                        if job.is_alive():
                            time.sleep(5)
                        else:
                            break
                        
                    if job.is_alive():
                        print('timeout exceeded... terminating job')
                        job.terminate()

                time.sleep(2)

            for site in return_dict[extn]:
                result_dict[extn].append(site)

            f = open("adblock_detect_custom.json", "w")
            json.dump(result_dict, f)
            f.close()

        except KeyboardInterrupt:
            print('Interrupted')
    
            f = open("adblock_detect_custom.json", "w")
            json.dump(result_dict, f)
            f.close()
            
            try:
                sys.exit(130)
            except SystemExit:
                os._exit(130)

        except Exception as e:
            print(e)
    
            f = open("adblock_detect_custom.json", "w")
            json.dump(result_dict, f)
            f.close()

    vdisplay.stop()
