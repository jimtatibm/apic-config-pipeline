import os, json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

FILE_NAME = "utils.py"
INFO = "[INFO]["+ FILE_NAME +"] - " 

def get_toolkit_credentials(CONFIG_FILES_DIR):
    toolkit_credentials = None
    if os.path.isfile(CONFIG_FILES_DIR + "/toolkit-creds.json"):
        with open(CONFIG_FILES_DIR + "/toolkit-creds.json") as f:
            toolkit_credentials = json.load(f)
    else:
        toolkit_credentials = {}
    return toolkit_credentials

def get_bearer_token(apic_url, apic_username, apic_password, apic_realm, apic_rest_clientid, apic_rest_clientsecret): 

    try:
        url = apic_url + "/api/token"
        reqheaders = {
            "Content-Type" : "application/json",
            "Accept" : "application/json"
        }

        reqJson = {
            "username": apic_username,
            "password": apic_password,
            "realm": apic_realm,
            "client_id": apic_rest_clientid,
            "client_secret": apic_rest_clientsecret,
            "grant_type": "password"
        }
        print(INFO + "Get Bearer Token")
        print(INFO + "----------------")
        print(INFO + "Url:", url)
        print(INFO + "Username:", apic_username)
        print(INFO + "Client ID:", apic_rest_clientid)
        s = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504 ])
        s.mount(apic_url, HTTPAdapter(max_retries=retries))

        response = s.post(url, headers=reqheaders, json=reqJson, verify=False, timeout=20)
        print("this is the response's status_code", response.status_code)
        resp_json = response.json()
        print("this is the response in json", resp_json)
        return resp_json
    except Exception as e:
        raise Exception("[ERROR] - Exception in " + FILE_NAME + ": " + repr(e))