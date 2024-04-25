# Benchmarking adblocking extensions across different user concerns
The repository contains the web crawling code for collecting and processing web data across different metrics such as performance, breakages, etc. We also provide the code for generating the website testing pool which comprises of landing as well as inner pages of websites.

- [Benchmarking adblocking extensions](#benchmarking-adblocking-extensions-across-different-user-concerns)
  - [Introduction](#introduction)
    - [Research](#research)
  - [Setup](#setup)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [User Concerns](#crawler-usage)
    - [Performance](#performance)
    - [Web Compatibility](#web-compatibility)
    - [Extension effectiveness](#extension-effectiveness)
    - [Data and Privacy Policy](#data-and-privacy-policy)
    - [Default configurations](#default-configuration)
  - [References](#references)

# Introduction
The repo is organized in a manner where the parent directory contains setup instructions and each subdirectory contains code for different user concerns. Since each user concern requires different approach, we have not combined them into a single tool and organized them separately. Researchers are free to pick up code bits that they deem useful.

## Research
This code has been used to obtain (fully/partially) the results of following research articles:
- [`From User Insights to Actionable Metrics: A User-Focused Evaluation of Privacy-Preserving Browser Extensions`](https://doi.org/10.1145/3634737.3657028) - AsiaCCS 2024

**Note:** This code is for research purposes and not a production level code. Hence it could have bugs/issues. Please feel free to raise issues on the repo or contact the author directly. Pull requests are also welcome and will be entertained.

# Setup

## Prerequisites

## Installation

# User Concerns
In our paper [1], we identify five major concerns that users often highlight in the user reviews. Further we develop new benchmarking techniques and improve the existing ones to evaluate the effectiveness of adblocking extensions in addressing those concerns.

## Performance
Some of the performance measurement code skeleton has been borrowed from the work done by Borgolte et al. [2].

## Web Compatibility

## Extension effectiveness

## Data and Privacy Policy

## Default configurations

# References
[1] Roongta, R., & Greenstadt, R. (2024). [From User Insights to Actionable Metrics: A User-Focused Evaluation of Privacy-Preserving Browser Extensions](https://doi.org/10.1145/3634737.3657028). In Proceedings of the ACM Asia Conference on Computer and Communications Security (ASIA CCS ’24).

[2] K Borgolte and N Feamster. (2020). [Understanding the Performance Costs and Benefits of Privacy-focused Browser Extensions](https://kevin.borgolte.me/files/pdf/www2020-privacy-extensions.pdf). In WWW' 20.