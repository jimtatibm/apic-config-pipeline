import os, json
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
import utils

FILE_NAME = "api_calls.py"
INFO = "[INFO]["+ FILE_NAME +"] - " 
DEBUG = os.getenv('DEBUG','')

def make_api_call(url, bearer_token, verb, data=None):

    try:
        if data:
            reqheaders = {
                "Accept" : "application/json",
                "Content-Type" : "application/json",
                "Authorization" : "Bearer " + bearer_token
            }
        else:
           reqheaders = {
                "Accept" : "application/json",
                "Authorization" : "Bearer " + bearer_token
            } 
        s = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        s.mount(url, HTTPAdapter(max_retries=retries))

        if verb == "get":
            if data:
                response = s.get(url, headers=reqheaders, json=data, verify=False, timeout=300)
            else:
                response = s.get(url, headers=reqheaders, verify=False, timeout=300)
        if verb == "post":
            if data:
                response = s.post(url, headers=reqheaders, json=data, verify=False, timeout=300)
            else:
                response = s.post(url, headers=reqheaders, verify=False, timeout=300)

        if DEBUG:
            print(INFO + "This is the request made:")
            print(utils.pretty_print_request(response.request))
            print(INFO + "This is the response's status_code", response.status_code)
            print(INFO + "This is the response in json", json.dumps(response.json(), indent=4, sort_keys=False))

    except Exception as e:
        raise Exception("[ERROR] - Exception in " + FILE_NAME + ": " + repr(e))

    return response