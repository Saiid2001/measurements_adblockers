from browsermobproxy import Server
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time 

# Initialize BrowserMob Proxy
server = Server("/home/ritik/work/pes/browsermob-proxy/bin/browsermob-proxy")
server.start()
proxy = server.create_proxy()

# Initialize Selenium
options = Options()
# options.add_argument('headless=new')
options.add_argument('ignore-certificate-errors')
options.add_argument("--proxy-server={0}".format(proxy.proxy))
options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36") 
# options.add_extension('/home/ritik/work/pes/extensions/extn_crx/ublock.crx')
# options.add_extension("/home/seluser/measure/harexporttrigger-0.6.3.crx")
options.binary_location = "/home/ritik/work/pes/chrome_113/chrome"
driver = webdriver.Chrome(options=options)
time.sleep(2)

# Create a new HAR with the following options
proxy.new_har("example", options={'captureHeaders': True, 'captureContent': True})

# Use Selenium to navigate to a webpage
driver.get("http://www.youtube.com")
time.sleep(2)

curr_scroll_position = -1
curr_time = time.time()
while True:
    # Define the scroll step size
    scroll_step = 50  # Adjust this value to control the scroll speed
    # Get the current scroll position
    scroll_position = driver.execute_script("return window.pageYOffset;")
    print(scroll_position)
    # Check if we've reached the bottom
    if curr_scroll_position == scroll_position:
        break
    else:
        curr_scroll_position = scroll_position

    # Scroll down by the step size
    driver.execute_script(f"window.scrollBy(0, {scroll_step});")
    
    # Wait for a bit (this controls the scroll speed indirectly)
    time.sleep(0.1)  # Adjust this value to control the scroll speed
    print(time.time() - curr_time)
    if time.time() - curr_time >= 2:
        break

# Collect HAR data
result = proxy.har

# Analyze HAR data (this is a simplified example)
total_size = 0
for entry in result['log']['entries'][:2]:
    print(entry)
    total_size += entry['response']['bodySize']
print(len(result['log']['entries']))
print(f"Total data usage: {total_size} bytes")

# Stop Selenium and BrowserMob Proxy
driver.quit()
server.stop()
