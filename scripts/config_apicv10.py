import os, json
import utils
import api_calls

"""

API Connect v10 post install configuration steps --> https://www.ibm.com/docs/en/api-connect/10.0.x?topic=environment-cloud-manager-configuration-checklist

"""

FILE_NAME = "config_apicv10.py"
STEP = 1
INFO = "[INFO]["+ FILE_NAME +"][STEP " + str(STEP) + "] - " 
DEBUG = os.getenv('DEBUG','')

try:

######################################################################################
# Step 1 - Get the IBM API Connect Toolkit credentials and environment configuration #
######################################################################################

    toolkit_credentials = utils.get_toolkit_credentials(os.environ["CONFIG_FILES_DIR"])
    environment_config = utils.get_env_config(os.environ["CONFIG_FILES_DIR"])
    if DEBUG:
        print(INFO + "These are the IBM API Connect Toolkit Credentials")
        print(INFO + "-------------------------------------------------")
        print(INFO, json.dumps(toolkit_credentials, indent=4, sort_keys=False))
        print(INFO + "These is the environment configuration")
        print(INFO + "--------------------------------------")
        print(INFO, json.dumps(environment_config, indent=4, sort_keys=False))

###############################################################
# Step 2 - Get the IBM API Connect Cloud Manager Bearer Token #
###############################################################
    STEP = 2
    
    admin_bearer_token = utils.get_bearer_token(environment_config["APIC_ADMIN_URL"],
                                                    "admin",
                                                    environment_config["APIC_ADMIN_PASSWORD"],
                                                    "admin/default-idp-1",
                                                    toolkit_credentials["toolkit"]["client_id"],
                                                    toolkit_credentials["toolkit"]["client_secret"])
    if DEBUG:
        print(INFO + "This is the Bearer Token to work against the IBM API Connect Management endpoints")
        print(INFO + "---------------------------------------------------------------------------------")
        print(INFO, admin_bearer_token)

#################################
# Step 3 - Get the Admin org ID #
#################################
    STEP = 3
    
    url = 'https://' + environment_config["APIC_ADMIN_URL"] + '/api/cloud/orgs'

    response = api_calls.make_api_call(url, admin_bearer_token, 'get')
    
    found = False
    admin_org_id = ''
    if response.status_code != 200:
          raise Exception("Return code for getting the Admin org ID isn't 200. It is " + str(response.status_code))
    for org in response.json()['results']:
        if org['org_type'] == "admin":
            found = True
            admin_org_id = org['id']
    if not found:
        raise Exception("[ERROR] - The Admin Organization was not found in the IBM API Connect Cluster instance")
    if DEBUG:
        print(INFO + "Admin Org ID: " + admin_org_id)

####################################
# Step 4 - Create the Email Server #
####################################
    STEP = 4
    
    url = 'https://' + environment_config["APIC_ADMIN_URL"] + '/api/orgs/' + admin_org_id + '/mail-servers'
    
    # Create the data object
    data = {}
    data['title'] = 'Default Email Server'
    data['name'] = 'default-email-server'
    data['host'] = os.environ['EMAIL_HOST']
    data['port'] = int(os.environ['EMAIL_PORT'])
    credentials = {}
    credentials['username'] = os.environ['EMAIL_USERNAME']
    credentials['password'] = os.environ['EMAIL_PASSWORD']
    data['credentials'] = credentials
    data['tls_client_profile_url'] = None
    data['secure'] = False

    if DEBUG:
        print(INFO + "This is the data object:")
        print(INFO, data)
        print(INFO + "This is the JSON dump:")
        print(INFO, json.dumps(data))

    response = api_calls.make_api_call(url, admin_bearer_token, 'post', data)

    email_server_url = ''
    if response.status_code != 201:
          raise Exception("Return code for creating the Email Server isn't 201. It is " + str(response.status_code))
    email_server_url = response.json()[url]
    if DEBUG:
        print(INFO + "Email Server url: " + email_server_url)

except Exception as e:
    raise Exception("[ERROR] - Exception in " + FILE_NAME + ": " + repr(e))