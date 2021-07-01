import os, json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

FILE_NAME = "utils.py"
INFO = "[INFO]["+ FILE_NAME +"] - " 
DEBUG = os.getenv('DEBUG','')

def get_toolkit_credentials(CONFIG_FILES_DIR):
    toolkit_credentials = None
    if os.path.isfile(CONFIG_FILES_DIR + "/toolkit-creds.json"):
        with open(CONFIG_FILES_DIR + "/toolkit-creds.json") as f:
            toolkit_credentials = json.load(f)
    else:
        toolkit_credentials = {}
    return toolkit_credentials

def get_env_config(CONFIG_FILES_DIR):
    env_config = None
    if os.path.isfile(CONFIG_FILES_DIR + "/config.json"):
        with open(CONFIG_FILES_DIR + "/config.json") as f:
            env_config = json.load(f)
    else:
        env_config = {}
    return env_config

def pretty_print_request(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print(INFO + "---------- Request start ----------")
    print(INFO + req.method + ' ' + req.url)
    for k, v in req.headers.items():
        print(INFO + '{}: {}'.format(k, v))
    print(INFO, req.body)
    print(INFO + "---------- Request end ----------")

def get_bearer_token(apic_url, apic_username, apic_password, apic_realm, apic_rest_clientid, apic_rest_clientsecret): 

    try:
        url = "https://" + apic_url + "/api/token"
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
        if DEBUG:
          print(INFO + "Get Bearer Token")
          print(INFO + "----------------")
          print(INFO + "Url:", url)
          print(INFO + "Username:", apic_username)
          print(INFO + "Client ID:", apic_rest_clientid)
        s = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504 ])
        s.mount(url, HTTPAdapter(max_retries=retries))
        response = s.post(url, headers=reqheaders, json=reqJson, verify=False, timeout=20)
        resp_json = response.json()
        if DEBUG:
          print(INFO + "This is the request made:")
          print(pretty_print_request(response.request))
          print(INFO + "This is the response's status_code:", response.status_code)
          print(INFO + "This is the response in json:", resp_json)
        if response.status_code != 200:
          raise Exception("Return code for getting the Bearer token isn't 200. It is " + str(response.status_code))
        return resp_json['access_token']
    except Exception as e:
        raise Exception("[ERROR] - Exception in " + FILE_NAME + ": " + repr(e))