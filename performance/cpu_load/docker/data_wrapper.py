# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import logging.config
import random
import re
import subprocess
import time
import uuid
import threading
import multiprocessing

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def run(log, browser, metric, inner_dict, domains, cpu):
    for domain in domains:
        # We always visit with the website without any extensions first to
        # warm up the upstream DNS cache.
        
        # COMMENTING THE NEXT LINE JUST FOR USER-AGENT CASE. UNCOMMENT IT AFTER
        # run_configuration(log, browser, "", domain, cpu)

        # random.shuffle(configurations)
        # for extension in configurations:
        #     run_configuration(log, browser, extension, domain, cpu)
        run_configuration(log, browser, inner_dict, domain, cpu)


def run_configuration(log, browser, inner_dict, domain, cpu):
    log.info(f"Collecting mpstat data via {browser} for '{domain}' on cpu '{cpu}'")
    try:
        get_domain(log, browser, inner_dict, domain, cpu)

    except Exception as e:
        log.error(f"Unknown error for domain '{domain}': {e}")


def get_domain(log, browser, inner_dict, domain, cpu):
    try:
        # cmd = ["docker", "run", "--rm",
        #         "-v", "/dev/shm:/dev/shm",
        #         "-v", "./chrome/data:/data",
        #         "--cpuset-cpus", cpu,
        #        "--security-opt", "seccomp=seccomp.json",
        #        f"mpstat-{browser}",
        #        "--extensions", extension, "--cpu", cpu, domain]
        # print(f'wrapper --- {inner_dict[domain]}')
        cmd = ["docker", "run", "--rm",
                "-v", "/dev/shm:/dev/shm",
                "-v", "./chrome/data:/data",
               "--security-opt", "seccomp=seccomp.json",
               f"mpstat-{browser}",
                str(inner_dict[domain])]
        # we can use "--shm-size=2g" instead of /dev/shm:/dev/shm
        
        run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        log.error(f"Error in container for '{domain}': {e.output}")
    
    stdout = run.stdout.decode('utf-8')
    stderr = run.stderr.decode('utf-8')
    print('STDOUT:', stdout) 
    print('STDERR:', stderr)
    log.info(stdout)
    log.error(stderr)
    
    #try:
    #    har = run.stdout.decode('utf-8')
    #except Exception as e:
    #    log.error(f"Error decoding output for domain {domain}: {e}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('log', default="logs/measurement.log")
    #parser.add_argument('database_config_file')
    parser.add_argument('domains_list_file')
    parser.add_argument('metric')
    parser.add_argument('browser')
    args = parser.parse_args()

    logging.basicConfig(filename=args.log, level=logging.DEBUG)
    log = logging.getLogger('wrapper')

    #database = Database.init_from_config_file(args.database_config_file)   
    if args.metric not in ('data', 'ram', 'cpu'):
        raise ValueError(f"Browser must be 'data', 'ram', or 'cpu', not '{args.metric}'")

    if args.browser not in ('firefox', 'chrome'):
        raise ValueError(f"Browser must be 'firefox' or 'chrome', not '{args.browser}'")

    domains = []
    # domains = ['http://www.google.com']
    with open(args.domains_list_file, 'r') as f:
        inner_dict = json.load(f)
    f.close()

    domains = list(inner_dict.keys())

    # RUNNING 4 DOCKERS ON 4 DIFFERENT CPU CORES
    # cpus_list = ['0','1','2','3']
    cpus_list = [str(cpu) for cpu in range(20)]
    thread_list = []
    domain_set = list(divide_chunks(domains, int(len(domains)/len(cpus_list))))
    for i in range(len(cpus_list)):
        # thread_list.append(threading.Thread(target=run, args=(log, args.browser, extensions_configurations, domain_set[i], cpus_list[i],)))
        thread_list.append(multiprocessing.Process(target=run, args=(log, args.browser, args.metric, inner_dict, domain_set[i], cpus_list[i],)))
    
    log.info("starting threads ....")
    for thread in thread_list:
        log.info(f"Starting run for '{thread}'")
        start_time = time.time()
        print('thread starts')
        thread.start()
        log.info(f"Elapsed time: {time.time() - start_time} seconds for '{thread}'")

    log.info("joining threads ....")
    for thread in thread_list:
        print('thread joins')
        thread.join()


if __name__ == '__main__':
    main()
