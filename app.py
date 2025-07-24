import re,requests,os,json
from flask import Flask,jsonify

app=Flask(__name__)

# Load configuration from config.json. If file not found or invalid, use empty default.
try:C=json.load(open("config.json"))
except(FileNotFoundError,json.JSONDecodeError)as e:C={"routers":[]}

# Function to fetch data from a given URL
def fd(u):
 try:
  r=requests.get(u,timeout=5) # Make HTTP GET request
  return""if r is None else(r.raise_for_status()or r.text) # Return text if successful, else empty string
 except requests.exceptions.RequestException:return"" # Return empty string on request error

# Function to parse uptime string
def pup(d):
 m=re.search(r"up\s+((?:\d+\s+day(?:s)?,\s+)?\d+:\d+)",d); # Regex to find uptime pattern
 if not m:return"N/A" # Return N/A if pattern not found
 u=m.group(1).strip();D,H,M=0,0,0 # Extract uptime string, initialize days, hours, minutes
 if'day'in u: # Check if days are present in uptime string
  D=int(re.search(r'\d+',u.split(',')[0]).group());H,M=map(int,u.split(',')[1].split(':')) # Parse days, hours, minutes
 else:H,M=map(int,u.split(':')) # Parse hours, minutes if no days
 ft=[] # List to store formatted time parts
 if D:ft.append(f"{D}d") # Add days if > 0
 if H%24:ft.append(f"{H%24}h") # Add hours if > 0 (modulo 24 for clean display)
 if M%60:ft.append(f"{M%60}m") # Add minutes if > 0 (modulo 60 for clean display)
 return"".join(ft)or"0m" # Join parts or return "0m" if all are zero

# Function to parse SSID and client station dump data
def psc(d):
 s,c={},[] # ssids dictionary, clients list
 L=d.splitlines();i=0 # Get lines, initialize line index
 while i<len(L): # Loop through lines
  l=L[i].strip();im=re.match(r"Interface\s+(\S+)",l) # Check for interface line
  if im: # If interface found
   n=im.group(1) # Get interface name
   for j in range(i+1,min(i+5,len(L))): # Look for SSID in next few lines
    sm=re.match(r"ssid\s+(\S+)",L[j].strip()) # Check for SSID line
    if sm:s[n]=sm.group(1);break # If SSID found, store it and break
   i+=1;continue # Move to next line, continue main loop
  stm=re.match(r"Station\s+([0-9a-fA-F:]{17})\s+\(on\s+(\S+)\)",l) # Check for station (client) line
  if stm: # If station found
   mac=stm.group(1).lower();iface=stm.group(2) # Extract MAC and interface
   ci={"mac":mac,"interface":iface};j=i+1 # Create client info dict, move to next line
   while j<len(L): # Loop through client's details
    nl=L[j].strip() # Get next line
    # Check for end of client block or start of new block
    if re.match(r"Station\s+([0-9a-fA-F:]{17})",nl)or re.match(r"Interface\s+(\S+)",nl)or re.match(r"phy#\d+",nl):break 
    rm=re.match(r"rx bytes:\s+(\d+)",nl);tm=re.match(r"tx bytes:\s+(\d+)",nl);cm=re.match(r"connected time:\s+(\d+)\s+seconds",nl) # Regex for rx/tx/connected time
    if rm:ci["rx_bytes"]=int(rm.group(1)) # Parse rx bytes
    if tm:ci["tx_bytes"]=int(tm.group(1)) # Parse tx bytes
    if cm:ci["connected_time"]=int(cm.group(1)) # Parse connected time
    j+=1 # Move to next line
   c.append(ci);i=j-1 # Add client info to list, update main loop index
  i+=1 # Move to next line
 return s,c # Return SSIDs and clients

# Function to parse DHCP leases
def pdhcp(d):
 d_i={} # DHCP info dictionary
 for l in d.splitlines(): # Loop through lines
  p=l.strip().split() # Split line into parts
  if len(p)>=4:mac=p[1].lower();ip=p[2];h=p[3];e={"ip":ip}; # Extract MAC, IP, hostname
  if h!='*':e["hostname"]=h # If hostname is not '*', add it
  d_i[mac]=e # Store DHCP entry by MAC
 return d_i

# Function to format bytes into human-readable string
def fb(v):
 if v is None:return"N/A" # Return N/A if value is None
 v=float(v) # Convert to float
 for u in['Bytes','KB','MB','GB','TB']: # Iterate through units
  if v<1024.0:return f"{v:.1f} {u}" # Return formatted string if within unit range
  v/=1024.0 # Divide by 1024 for next unit
 return f"{v:.1f} PB" # Return in Petabytes if very large

# Function to format seconds into human-readable time
def ft(s):
 if s is None:return"N/A" # Return N/A if value is None
 s=int(s);m=s//60;h=m//60;d=h//24 # Convert to int, calculate minutes, hours, days
 f_=[] # List to store formatted time parts
 if d:f_.append(f"{d}d") # Add days if > 0
 if h%24:f_.append(f"{h%24}h") # Add hours if > 0 (modulo 24 for clean display)
 if m%60:f_.append(f"{m%60}m") # Add minutes if > 0 (modulo 60 for clean display)
 return"".join(f_)or"0m" # Join parts or return "0m" if all are zero

# Main API route for OpenWrt stats
@app.route('/api/openwrt')
def openwrt_stats():
    ups,cbs,ids,dhl={},{},set(),{} # Initialize uptimes, clients by SSID, identified SSIDs, DHCP leases

    # Fetch and parse DHCP leases from router1 (if configured)
    r1_d_u=next((r.get("dhcp_url")for r in C["routers"]if r.get("id")=="router1"and"dhcp_url"in r),None)
    if r1_d_u and (r1d_data_:=fd(r1_d_u)):dhl.update(pdhcp(r1d_data_))

    # Iterate through configured routers
    for rc in C["routers"]:
        rid=rc.get("id");ri_u=rc.get("info_url") # Get router ID and info URL
        if not rid or not ri_u:continue # Skip if essential info missing
        r_data_=fd(ri_u) # Fetch router info data
        if not r_data_:continue # Skip if data fetch fails
        ups[f"{rid} uptime"]=pup(r_data_) # Parse and store router uptime
        ssids,clients=psc(r_data_) # Parse SSIDs and clients for this router
        ids.update(s.replace(" ","_").lower() for s in ssids.values()) # Add SSIDs to overall identified set
        for c in clients: # Process each client
            ssid_k=ssids.get(c["interface"],"unknown_ssid").replace(" ","_").lower() # Get SSID key for client
            # Add client info to clients_by_ssid, resolving hostname/IP/MAC
            cbs.setdefault(ssid_k,[]).append({"hostname":dhl.get(c["mac"],{}).get("hostname",dhl.get(c["mac"],{}).get("ip",c["mac"])),"rx/tx":f"{fb(c.get('rx_bytes'))} / {fb(c.get('tx_bytes'))}","uptime":ft(c.get('connected_time'))})
    
    f_out={**ups} # Start final output with uptimes
    s_out=ids.union(cbs.keys()) # Combine all identified SSIDs
    for ssid_k in sorted(list(s_out)):f_out[ssid_k]=f"[{len(cbs.get(ssid_k,[]))}]" # Add SSID client counts
    if"unknown_ssid"in cbs:f_out["unknown_ssid"]=f"[{len(cbs['unknown_ssid'])}]" # Add unknown SSID count if present
    f_out["total clients"]=sum(len(c) for c in cbs.values()) # Calculate total clients
    for ssid_k in sorted(list(s_out)):cbs.setdefault(ssid_k,[]) # Ensure all SSIDs are present in clients dict (even if empty)
    f_out["clients"]=cbs # Add detailed client data
    return jsonify(f_out) # Return JSON response

# Main entry point: run Flask app if script is executed directly
if __name__ == '__main__':
    h=C.get("server",{}).get("host");p=C.get("server",{}).get("port") # Get host and port from config
    if h and p:app.run(host=h,port=p) # Run app if host and port are valid
    else:print("E: Missing host/port in config.json.");exit(1) # Exit if host/port are missing
