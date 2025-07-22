Wi-Fi Client Monitor
A Flask-based web application to monitor Wi-Fi clients and network statistics from OpenWrt routers. This project provides a dashboard to view connected devices, their associated SSIDs, and real-time network traffic on your routers.

Features
Client Monitoring: Displays connected Wi-Fi clients, their MAC addresses (or resolved hostnames/IPs), and the SSID they are connected to.

Real-time Network Statistics: Shows current download/upload bytes and rates for network interfaces on your OpenWrt routers.

Multi-Router Support: Configurable to pull data from multiple OpenWrt routers.

Data Persistence: Stores historical client and network statistics in an SQLite database.

Theming: Supports light and dark mode based on system preferences.

Production-Ready Deployment: Includes instructions for deploying with Gunicorn and Nginx.

Architecture
OpenWrt Routers: Host simple CGI scripts to expose Wi-Fi client and network interface data.

Flask Application (app.py): The Python backend that fetches data from OpenWrt CGI scripts, processes it, stores it in an SQLite database, and serves JSON API endpoints and HTML templates.

Gunicorn: A Python WSGI HTTP Server that runs the Flask application in a production environment.

Systemd: Manages the Gunicorn process, ensuring it starts on boot and restarts automatically.

Nginx: A high-performance web server and reverse proxy that handles incoming web requests, serves static files efficiently, and forwards dynamic requests to Gunicorn.

Prerequisites
On your OpenWrt Router(s):
OpenWrt firmware installed.

SSH access enabled.

iw utility installed (usually comes by default, but confirm if iw dev <interface> station dump works).

On your Armbian/Linux Server (or any machine with Python 3):
Python 3.8+ installed.

python3-venv package installed (for creating virtual environments).

sudo or root privileges for system-level configurations.

Network connectivity to your OpenWrt router(s).

Setup Guide
Follow these steps to get your Wi-Fi Client Monitor up and running.

Step 1: Set up OpenWrt CGI Scripts
These scripts will be placed on your OpenWrt router(s) in the /www/cgi-bin/ directory.

SSH into your OpenWrt Router(s):

ssh root@YOUR_OPENWRT_ROUTER_IP

(Replace YOUR_OPENWRT_ROUTER_IP with your router's actual IP address, e.g., 192.168.1.1)

Navigate to the CGI-BIN Directory:

cd /www/cgi-bin/

Create get_ssids.sh:

nano get_ssids.sh

Paste the content from the OpenWrt SSID Script (get_ssids.sh) section below. Save and exit.

Create get_clients.sh:

nano get_clients.sh

Paste the content from the OpenWrt Clients Script (get_clients.sh) section below. Save and exit.

Create get_dhcp_leases.sh:

nano get_dhcp_leases.sh

Paste the content from the OpenWrt DHCP Leases Script (get_dhcp_leases.sh) section below. Save and exit.

Create get_net_stats.sh:

nano get_net_stats.sh

Paste the content from the OpenWrt Network Stats Script (get_net_stats.sh) section below. Save and exit.

Make Scripts Executable:

chmod +x get_ssids.sh
chmod +x get_clients.sh
chmod +x get_dhcp_leases.sh
chmod +x get_net_stats.sh

Verify Scripts (Optional but Recommended):
Open your web browser and try to access them:

http://YOUR_OPENWRT_ROUTER_IP/cgi-bin/get_ssids.sh

http://YOUR_OPENWRT_ROUTER_IP/cgi-bin/get_clients.sh

http://YOUR_OPENWRT_ROUTER_IP/cgi-bin/get_dhcp_leases.sh

http://YOUR_OPENWRT_ROUTER_IP/cgi-bin/get_net_stats.sh
You should see plain text output. If you get a "404 Not Found" or "Permission Denied" error, double-check the file paths and permissions.

Step 2: Set up the Python Flask Backend Server (on Armbian/Linux)
SSH into your Armbian/Linux Server:

ssh user@YOUR_ARMBIAN_SERVER_IP

(Replace user with your actual username and YOUR_ARMBIAN_SERVER_IP with your server's IP address)

Create Project Directory and Set Permissions:

sudo mkdir -p /var/www/wifi_client_app
sudo chown -R www-data:www-data /var/www/wifi_client_app
sudo chmod -R ug+rwX /var/www/wifi_client_app
# If 'www-data' user/group does not exist, create it:
# sudo adduser www-data

Navigate to the Project Directory:

cd /var/www/wifi_client_app/

Install Python3 and venv (if not already installed):

sudo apt update
sudo apt install python3 python3-venv -y

Create and Activate a Python Virtual Environment:

python3 -m venv venv
source venv/bin/activate

You should see (venv) prefix in your terminal prompt.

Create requirements.txt:

nano requirements.txt

Paste the content from the Python Dependencies (requirements.txt) section below. Save and exit.

Install Python Dependencies:

python -m pip install -r requirements.txt

Create app.py:

nano app.py

Paste the content from the Python Flask Server (app.py) section below. Save and exit.

Create config.json:

nano config.json

Paste the content from the Configuration File (config.json) section below.
Important: Edit the router_ips, dhcp_leases_cgi_url, and ignored_interfaces values in config.json to match your specific network setup.
Save and exit.

Create templates and static directories with subdirectories:

mkdir -p templates static/css static/js

Create templates/index.html:

nano templates/index.html

Paste the content from the Main Dashboard HTML (index.html) section below. Save and exit.

Create templates/net_stats.html:

nano templates/net_stats.html

Paste the content from the Network Statistics HTML (net_stats.html) section below. Save and exit.

Create static/js/script.js:

nano static/js/script.js

Paste the content from the Main Dashboard JavaScript (script.js) section below. Save and exit.

Create static/js/net_stats_script.js:

nano static/js/net_stats_script.js

Paste the content from the Network Statistics JavaScript (net_stats_script.js) section below. Save and exit.

Create static/css/style.css:

nano static/css/style.css

Paste the content from the Custom CSS (style.css) section below. Save and exit.

Step 3: Configure Gunicorn with Systemd
Create Gunicorn Log Directory:

sudo mkdir -p /var/log/wifi-monitor
sudo chown www-data:www-data /var/log/wifi-monitor

Create the Systemd Service File:

sudo nano /etc/systemd/system/wifi-monitor.service

Paste the content from the Systemd Service File (wifi-monitor.service) section below. Save and exit.

Reload Systemd Daemon:

sudo systemctl daemon-reload

Enable and Start the Gunicorn Service:

sudo systemctl enable wifi-monitor.service
sudo systemctl start wifi-monitor.service

Check Service Status:

sudo systemctl status wifi-monitor.service

Ensure it shows Active: active (running). If not, check /var/log/wifi-monitor/error.log for details.

Step 4: Install and Configure Nginx as a Reverse Proxy
Install Nginx:

sudo apt update
sudo apt install nginx -y

Create Nginx Configuration File:

sudo nano /etc/nginx/sites-available/wifi-monitor

Paste the content from the Nginx Configuration section below.
IMPORTANT:

Replace wifi.home with your desired domain name (if you have one) or remove it.

Replace YOUR_ARMBIAN_SERVER_IP with the actual IP address of your Armbian server.
Save and exit.

Create a Symlink to Enable the Nginx Configuration:

sudo ln -s /etc/nginx/sites-available/wifi-monitor /etc/nginx/sites-enabled/

Remove the Default Nginx Configuration (if it exists):

sudo rm /etc/nginx/sites-enabled/default

Test Nginx Configuration Syntax:

sudo nginx -t

You should see syntax is ok and test is successful.

Restart Nginx:

sudo systemctl restart nginx

Step 5: Configure DNS (Optional but Recommended)
If you want to access your Wi-Fi Monitor using http://wifi.home instead of an IP address:

On your router (OpenWrt):

Go to Network > DHCP and DNS.

Under the Static Leases tab, ensure your Armbian server has a static IP address.

Under the Hostnames tab (or similar), add a new entry:

Hostname: wifi.home

IP address: YOUR_ARMBIAN_SERVER_IP

Save and apply changes.

Restart the DNS service on your router (or reboot the router).

On your client device (PC/phone):

Ensure your device is using your OpenWrt router as its DNS server.

Clear your device's DNS cache if wifi.home doesn't resolve immediately.

Accessing the Dashboard
Open your web browser and navigate to:

http://YOUR_ARMBIAN_SERVER_IP (if you didn't set up DNS)

http://wifi.home (if you set up DNS)

You should now see your Wi-Fi Client Monitor dashboard!

Troubleshooting
"502 Bad Gateway" (Nginx error): Nginx can't connect to Gunicorn.

Check sudo systemctl status wifi-monitor.service to ensure Gunicorn is running.

Check Gunicorn logs: sudo cat /var/log/wifi-monitor/error.log

Ensure Gunicorn is bound to 127.0.0.1:5111 and Nginx proxy_pass matches.

"403 Forbidden" (Nginx error): Nginx might not have permission to read static files.

Double-check sudo chown -R www-data:www-data /var/www/wifi_client_app and sudo chmod -R ug+rwX /var/www/wifi_client_app.

"404 Not Found" (Nginx or Flask):

If for static files (/static/css/style.css), check Nginx location /static/ block and the alias path.

If for API endpoints, check Flask routes in app.py.

"Error fetching Wi-Fi clients" / "Data temporarily unavailable":

Check if your OpenWrt CGI scripts are accessible via browser (Step 1.8).

Verify the router_ips and dhcp_leases_cgi_url in config.json are correct.

Ensure your Armbian/Linux server can reach your OpenWrt router(s) (e.g., ping YOUR_OPENWRT_ROUTER_IP from the server).

Check the Flask app's logs: sudo cat /var/log/wifi-monitor/error.log.

"sqlite3.OperationalError: attempt to write a readonly database":

Ensure www-data user has write permissions to /var/www/wifi_client_app and its contents. Re-run sudo chown -R www-data:www-data /var/www/wifi_client_app and sudo chmod -R ug+rwX /var/www/wifi_client_app.
