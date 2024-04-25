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


def find_all_iframes(driver):
    iframes = driver.find_elements(By.XPATH, value=".//iframe | .//frame")
    return len(iframes)

def initialize_driver(extn, num_tries):
    while num_tries > 0:
        try:
            options = Options()
            extensions_path = pathlib.Path("../extensions/")
            options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
            options.binary_location = "../chrome_113/chrome"
            # service = Service(executable_path='/home/ritik/work/pes/chromedriver_113/chromedriver')
            version = '113.0.5672.0'
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

    ret_val = 0
    num_tries = 3

    try:
        for site in site_lst:
            driver.get(site)
            wait_until_loaded(driver)
            time.sleep(3)

            # ret_val = find_all_iframes(driver)
            ret_val += find_all_iframes(driver)

            if ret_val:
                break

    except Exception as e:
        print(e, key)
        num_tries -= 1
        if num_tries > 0:
            run(site_lst, extn, key, return_dict, lock, display)

    if len(site_lst) > 0:
        return_dict[extn][key] = round(ret_val/len(site_lst), 2)

    driver.quit()

# def run(sites, extn, return_dict, l, display):
#     input_str = ""
#     for site in sites:
#         input_str = input_str + site + ","
#     input_str = input_str[:-1]

#     fname = sites[0].split("//")[1]
#     if fname[:3] == 'www':
#         fname = fname[4:]
    
#     frames = []
#     docs = []
#     for i in range(3):
#         try:
#             cmd = ["node", "frames.js", input_str, extn, fname]
#             process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)#, timeout = 180)

#         except subprocess.TimeoutExpired as t:
#             print(f'Timeout for site: {site} {extn}')
#             return
        
#         except subprocess.CalledProcessError as e:
#             print(f'Error for site: {site} {extn}')
#             return

#         except Exception as e:
#             print(e)
#             continue
        
#         stdout = process.stdout.decode('utf-8')
#         stderr = process.stderr.decode('utf-8')
#         print('STDOUT:', stdout) 
#         print('STDERR:', stderr)
#         with open('log', 'a+') as f:
#             f.write(f'STDOUT: {stdout}\n') 
#             f.write(f'STDERR: {stderr}\n')
#         f.close()

#         if stderr == "":
#             frames.append(round(float(stdout.split()[2])))
#             docs.append(round(float(stdout.split()[3])))
            
#     if frames == []:
#         frames = [-1, -1, -1]
#     if docs == []:
#         docs = [-1, -1, -1]
 
        
#     try:
#         l.acquire()
#         # print(fname)
#         return_dict[extn][fname].extend([frames, docs])
#         l.release()
#     except Exception as e:
#         print(e)
#         l.release()
#     # if 'adblocker_detected' in stdout:
#     #     return_dict[extn].append(stdout.split()[1])

if __name__ == "__main__":
    extn_lst = ['adblock', 'control', 'ublock', 'privacy-badger',
           "decentraleyes",
           "disconnect",
           "ghostery",
           "adguard"]

    with open("../inner_pages_custom.json", "r") as f:
        updated_dict = json.load(f)
    f.close()

    SIZE = 10 # number of browser windows that will open

    latest_list = list(updated_dict.keys())[156:176]

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
        try:
            for i in range(len(chunks_list)):
                jobs = []
                for key in chunks_list[i]:
                    p = multiprocessing.Process(target=run, args=(updated_dict[key], extn, key, return_dict, multiprocessing.Lock(), display, ))
                    # p = multiprocessing.Process(target=run, args=(updated_dict[key], extn, key, return_dict, lock, display, ))
                    jobs.append(p)
                for job in jobs:
                    job.start()

                TIMEOUT = 1000
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

            for site in latest_list:
                print(return_dict[extn][site])
                for val in return_dict[extn][site]:
                    result_dict[extn][site].append(val)

            f = open('frames.json', 'w')
            json.dump(result_dict, f)
            f.close()


            # for site in return_dict[extn]:
            #     result_dict[extn].append(site)

            # f = open("adblock_detect_custom.json", "w")
            # json.dump(result_dict, f)
            # f.close()

        except KeyboardInterrupt:
            print('Interrupted')
    
            f = open('frames.json', 'w')
            json.dump(result_dict, f)
            f.close()
            
            try:
                sys.exit(130)
            except SystemExit:
                os._exit(130)
        
        except Exception as e:
            print(e)

            f = open('frames.json', 'w')
            json.dump(result_dict, f)
            f.close()

    vdisplay.stop()
