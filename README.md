# OpenWrt Router Stats API

This Flask application collects and aggregates client connection data (uptime, RX/TX bytes, hostname/IP) from multiple OpenWrt routers and presents it in a unified JSON format via a simple API endpoint.

## Table of Contents
1. [Features](#1-features)  
2. [Prerequisites](#2-prerequisites)  
3. [Setup and Installation](#3-setup-and-installation)  
   3.1. [Flask Application (app.py)](#31-flask-application-apppy)  
   3.2. [Configuration File (config.json)](#32-configuration-file-configjson)  
   3.3. [OpenWrt CGI Scripts](#33-openwrt-cgi-scripts)  
   - 3.3.1. [info.cgi](#331-infocgi)  
   - 3.3.2. [dhcp.cgi](#332-dhcpcgi)  
4. [Running the Application](#4-running-the-application)  
5. [Accessing the API](#5-accessing-the-api)  
6. [Troubleshooting and Error Handling](#6-troubleshooting-and-error-handling)  

---

## 1. Features
- Collects uptime for multiple OpenWrt routers.  
- Aggregates connected client data (MAC, interface, RX/TX bytes, connected time) from various Wi-Fi interfaces.  
- Resolves client hostnames using DHCP lease information (from a designated primary router).  
- Categorizes clients by SSID.  
- Provides total client count.  
- Presents all data in a single, easy-to-parse JSON API endpoint.  

---

## 2. Prerequisites

Before deploying, ensure you have:

- Python 3.x installed.  
- Flask and Requests Python libraries. Install them via pip:

```bash
pip install Flask requests
```

- OpenWrt Routers with SSH access to create and manage CGI scripts. The routers should expose `info.cgi` and `dhcp.cgi` (or similar) endpoints providing the required raw data.  

---

## 3. Setup and Installation

### 3.1. Flask Application (app.py)

The core Flask application logic is contained in `app.py`. This file is designed to be highly compact and relies on `config.json` for its runtime parameters.

You can find the `app.py` file in this repository.

### 3.2. Configuration File (config.json)

The `config.json` file defines your OpenWrt router endpoints and the Flask server's binding address and port. This file must be placed in the same directory as `app.py`.

You can find an example `config.json` in this repository.

**Example config.json structure:**

```json
{
  "routers": [
    {
      "id": "router1",
      "info_url": "http://192.168.1.1/cgi-bin/info.cgi",
      "dhcp_url": "http://192.168.1.1/cgi-bin/dhcp.cgi"
    },
    {
      "id": "router2",
      "info_url": "http://192.168.1.2/cgi-bin/info.cgi"
      // dhcp_url is optional for router2 if it doesn't serve DHCP leases
    }
  ],
  "server": {
    "host": "0.0.0.0",
    "port": 3001
  }
}
```

**Configuration Details:**

- `routers`: An array of router configurations.  
- `id` (string): A unique string identifier for the router (e.g., "main_router", "basement_ap").  
- `info_url` (string): The full HTTP URL to the `info.cgi` script on this OpenWrt router. This is mandatory.  
- `dhcp_url` (string, optional): The full HTTP URL to the `dhcp.cgi` script on this router. The application is designed to primarily use the `dhcp_url` from the router with `id: "router1"` for all client hostname lookups.  

- `server`: Configures the Flask server's listening interface.  
  - `host` (string): The IP address on which the Flask server will listen. Use `"0.0.0.0"` to listen on all available network interfaces, or a specific IP address like `"192.168.1.3"`. This is mandatory.  
  - `port` (integer): The port number on which the Flask server will listen (e.g., 3001). This is mandatory.  

---

### 3.3. OpenWrt CGI Scripts

You need to create these simple shell scripts on your OpenWrt routers. They should be placed in the `/www/cgi-bin/` directory on each router and made executable (`chmod +x <script_name>`).

#### 3.3.1. info.cgi

This script gathers wireless device information (`iw dev`), detailed client station dumps from specific wireless interfaces, and the router's uptime.

Save this content on your router as `/www/cgi-bin/info.cgi`:

```bash
#!/bin/sh
echo "Content-type: text/plain"
echo ""

echo "=== iw dev router1 ==="
iw dev

echo ""
echo "=== phy0-ap0 station dump router1 ==="
iw dev phy0-ap0 station dump

echo ""
echo "=== phy1-ap0 station dump router1 ==="
iw dev phy1-ap0 station dump

echo ""
echo "=== uptime router1 ==="
uptime
```

**Important Notes:**

- **Permissions**: After creating, make it executable: `chmod +x /www/cgi-bin/info.cgi`  
- **Device Names**: You must adjust `router1`, `phy0-ap0`, and `phy1-ap0` to match the actual device names and wireless interfaces on your specific OpenWrt router. You can find these names by running `iw dev` on your router's SSH console.  
- **Multiple Routers**: If you configure multiple routers in `config.json`, each router that needs `info_url` capabilities will require its own `info.cgi` script, adapted to its local device names.  

#### 3.3.2. dhcp.cgi

This script simply outputs the content of the DHCP lease file, which is crucial for hostname resolution.

Save this content on your router as `/www/cgi-bin/dhcp.cgi`:

```bash
#!/bin/sh
echo "Content-type: text/plain"
echo ""
cat /tmp/dhcp.leases
```

**Important Notes:**

- **Permissions**: After creating, make it executable: `chmod +x /www/cgi-bin/dhcp.cgi`  
- **Location**: The `dhcp.leases` file is typically located at `/tmp/dhcp.leases` on OpenWrt. Ensure this path is correct for your router.  
- **DHCP Server**: This script is primarily needed on the router(s) that act as your DHCP server and for which you want hostname resolution.  

---

## 4. Running the Application

- **Place Files**: Ensure `app.py` and `config.json` are in the same directory on your host machine (where you want to run the Flask app).  
- **Open Terminal**: Navigate to that directory in your terminal or command prompt.  
- **Execute**: Run the Flask application using:

```bash
python app.py
```

The application will start, and you should see output indicating it's running on the configured host and port:

```
 * Serving Flask app 'app'
 * Running on http://192.168.1.3:3001 # (Your configured host/port)
```

---

## 5. Accessing the API

Once the application is running, you can access the API endpoint in your web browser or using tools like `curl`:

```bash
curl http://<your_server_host>:<your_server_port>/api/openwrt
```

Replace `<your_server_host>` and `<your_server_port>` with the values you set in your `config.json` (e.g., `http://192.168.1.3:3001/api/openwrt`).

The API will return a JSON object containing aggregated statistics.

---

## 6. Troubleshooting and Error Handling

### E: Missing host/port in config.json.

- **Cause**: The `config.json` file is either missing, cannot be parsed (due to invalid JSON syntax), or the `host` or `port` keys are absent from the server section.  
- **Solution**: Verify that `config.json` is in the same directory as `app.py`, its name is spelled correctly, and its content is valid JSON matching the structure in this documentation (especially the `server` section with `host` and `port`).  

### Error loading config file: [Errno 2] No such file or directory: 'config.json':

- **Cause**: The `config.json` file was not found.  
- **Solution**: Ensure `config.json` is in the directory from which you are running `python app.py`.  

### Error loading config file: Expecting value: line X column Y (char Z):

- **Cause**: Your `config.json` file has a JSON syntax error.  
- **Solution**: Use a JSON validator (online tools are available) to check your `config.json` for errors.  

### requests.exceptions.ConnectionError / AttributeError: 'NoneType' object has no attribute 'text':

- **Cause**: The Flask application failed to connect to or fetch data from one of your router's CGI script URLs. This could be due to incorrect `info_url`/`dhcp_url` in `config.json`, network connectivity issues, or the CGI scripts on the router not running/accessible.  
- **Solution**:  
  - Verify the `info_url` and `dhcp_url` in your `config.json` are correct and accessible directly from the machine running the Flask app (e.g., open them in a browser or use `curl`).  
  - Check network connectivity between the Flask app host and your OpenWrt routers.  
  - Ensure the CGI scripts (`info.cgi`, `dhcp.cgi`) exist in `/www/cgi-bin/` on your routers and are executable (`chmod +x`).  
  - Check your router's firewall settings to ensure the web server (uHTTPd) is accessible from the Flask app host.  

