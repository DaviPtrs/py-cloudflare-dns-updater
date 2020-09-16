import requests
import json
import sys
import dotenv
import os

dotenv.load_dotenv()

# DEFINING GLOBAL VARIABLES

IP_API = 'https://api.ipify.org?format=json'
CF_ZONE = os.getenv('CF_ZONE')
CF_RECORD = os.getenv('CF_RECORD')
CF_RECORD_TTL = os.getenv('CF_RECORD_TTL', 1)
CF_RECORD_PROXIED = os.getenv('CF_RECORD_PROXIED', True)
CF_AUTH_EMAIL = os.getenv('CF_AUTH_EMAIL')
CF_AUTH_KEY = os.getenv('CF_AUTH_KEY')
HEADERS = {
    'X-Auth-Email': CF_AUTH_EMAIL,
    'X-Auth-Key': CF_AUTH_KEY,
    'Content-Type': 'application/json',
    }

def zone_id():
    url = f'https://api.cloudflare.com/client/v4/zones?name={CF_ZONE}&status=active'
    response = requests.get(url,headers=HEADERS)
    assert response.status_code == 200
    response = response.json()
    return response['result'][0]['id']

def record_id():
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id()}/dns_records?type=A&name={CF_RECORD}'
    response = requests.get(url,headers=HEADERS)
    assert response.status_code == 200
    response = response.json()
    return response['result'][0]['id']

try:
    ZONE_ID = zone_id()
    RECORD_ID = record_id()
except requests.ConnectionError as err:
    print("Unable to fetch Zone ID and/or Record ID. Check your internet connection")
    print(err)
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
    assert response.status_code == 200

def check_n_update():
    new_ip = actual_ip()
    old_ip = recorded_ip()
    if new_ip != old_ip:
        print(f"New ip: {new_ip}")
        print(f"Old ip: {old_ip}")
        print("Updating DNS Record...")
        update_dns_record()
        print("DNS Record updated!")

if __name__ == "__main__":
    connection_error_flag = False
    print("Checking differences between public IP and DNS Record IP")

    try:
        check_n_update()
        connection_error_flag = False
    except requests.ConnectionError:
        if not connection_error_flag:
            print("Error. Check your internet connection")
        connection_error_flag = True
    