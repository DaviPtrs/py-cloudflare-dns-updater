import requests
import json
import sys
import dotenv
import os
import time
import logging as log

dotenv.load_dotenv()
DEBUG = os.getenv('DEBUG')
if DEBUG:
    log_level = log.DEBUG
else:
    log_level = log.INFO
log.basicConfig(
    stream=sys.stdout, 
    level=log_level, 
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
    )
log.info("Initializing global parameters")

# DEFINING GLOBAL VARIABLES

IP_API = 'https://api.ipify.org?format=json'
CF_ZONE = os.getenv('CF_ZONE')
CF_RECORD = os.getenv('CF_RECORD')
CF_RECORD_TTL = int(os.getenv('CF_RECORD_TTL', 1))
CF_RECORD_PROXIED = bool(os.getenv('CF_RECORD_PROXIED', True))
CF_AUTH_EMAIL = os.getenv('CF_AUTH_EMAIL')
CF_AUTH_KEY = os.getenv('CF_AUTH_KEY')
TIME_INTERVAL = int(os.getenv('TIME_INTERVAL', 3600))
HEADERS = {
    'X-Auth-Email': CF_AUTH_EMAIL,
    'X-Auth-Key': CF_AUTH_KEY,
    'Content-Type': 'application/json',
    }

def zone_id():
    url = f'https://api.cloudflare.com/client/v4/zones?name={CF_ZONE}&status=active'
    response = requests.get(url,headers=HEADERS)
    log.debug(response)
    assert response.status_code == 200
    response = response.json()
    return response['result'][0]['id']

def record_id():
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id()}/dns_records?type=A&name={CF_RECORD}'
    response = requests.get(url,headers=HEADERS)
    log.debug(response)
    assert response.status_code == 200
    response = response.json()
    return response['result'][0]['id']

try:
    log.info('Fetching Zone Id')
    ZONE_ID = zone_id()
    log.debug(f'Zone Id: {ZONE_ID}')
    log.info('Fetching DNS Record Id')
    RECORD_ID = record_id()
    log.debug(f'DNS Record Id: {RECORD_ID}')
except requests.ConnectionError as err:
    log.error("Unable to fetch Zone ID and/or Record ID. Check your internet connection")
    log.error(err)
    sys.exit(1)

# END OF GLOBAL VARIABLE DEFINITION

def actual_ip():
    resp = requests.get(IP_API)
    assert resp.status_code == 200
    ip = resp.json()['ip']
    return ip

def recorded_ip():
    url = f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{RECORD_ID}'
    response = requests.get(url,headers=HEADERS)
    log.debug(response)
    assert response.status_code == 200
    response = response.json()
    return response['result']['content']

def update_dns_record():
    url = f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{RECORD_ID}'
    data = {
        "type": "A",
        'name': CF_RECORD,
        'content': actual_ip(),
        'ttl': CF_RECORD_TTL,
        'proxied': CF_RECORD_PROXIED,
    }
    response = requests.put(url,data=json.dumps(data),headers=HEADERS)
    log.debug(response)
    assert response.status_code == 200

def check_n_update():
    new_ip = actual_ip()
    old_ip = recorded_ip()
    if new_ip != old_ip:
        log.info("Public IP change detected")
        log.info(f"New ip: {new_ip}")
        log.info(f"Old ip: {old_ip}")
        log.info("Updating DNS Record...")
        update_dns_record()
        log.info("DNS Record updated!")

if __name__ == "__main__":
    connection_error_flag = False
    log.info("Public IP Change listener started")
    log.info(f"Time interval: {TIME_INTERVAL} seconds")
    while True:
        try:
            check_n_update()
            connection_error_flag = False
        except requests.ConnectionError:
            if not connection_error_flag:
                log.error("Error. Check your internet connection")
            connection_error_flag = True
        time.sleep(TIME_INTERVAL)
