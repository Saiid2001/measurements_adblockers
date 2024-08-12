# Performance

This folder has the code for measuring CPU, Data and RAM Usage. Follow the below procedures for respective metric.

## CPU Usage
Inside the docker folder, run the command `bash run.sh logs/ ../../websites_inner_pages.json cpu {#cpus} chrome`

The second argument is the website pool that can be altered. Pass a number in place `#cpus` to open multiple chrome browser instances according to your hardware capabilities. Currently the code only supports chrome but can be easily extended to firefox.

The data is stored inside `chrome/data` folder which can be processed using `process_cpu_data.py` script.

## RAM Usage
Inside the docker folder, run the command `bash run.sh logs/ ../../websites_inner_pages.json ram {#cpus} chrome`

The second argument is the website pool that can be altered. Pass a number in place `#cpus` to open multiple chrome browser instances. Currently the code only supports chrome but can be easily extended to firefox.

The data is stored inside `chrome/data` folder which can be processed using `process_ram_data.py` script.

## Data Usage
Inside the docker folder, run the command `python3 data_wrapper.py`. Data_usage doesn't require docker support.

The seconf argument is the website pool that can be altered. Pass a number in place `#cpus` to open multiple chrome browser instances. Currently the code only supports chrome but can be easily extended to firefox.

The data is stored inside `docker/data_usage` folder which can be processed using `process_data_usage.py` script.