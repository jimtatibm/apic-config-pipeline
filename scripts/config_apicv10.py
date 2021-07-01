import os, json
import utils
import api_calls

"""

API Connect v10 post install configuration steps --> https://www.ibm.com/docs/en/api-connect/10.0.x?topic=environment-cloud-manager-configuration-checklist

"""

FILE_NAME = "config_apicv10.py"
INFO = "[INFO]["+ FILE_NAME +"] - " 
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
    url = 'https://' + environment_config["APIC_ADMIN_URL"] + '/api/cloud/orgs'
    response = api_calls.make_api_call(url, admin_bearer_token, 'get')
    found = False
    admin_org_id = ''
    if response.status_code != 200:
          raise Exception("Return code for getting getting the Admin org ID isn't 200. It is " + str(response.status_code))
    for org in response.json()['results']:
        if org['org_type'] == "admin":
            found = True
            admin_org_id = org['id']
    if not found:
        raise Exception("[ERROR] - The Admin Organization was not found in the IBM API Connect Cluster instance")
    if DEBUG:
        print(INFO + "Admin Org ID: " + admin_org_id)

except Exception as e:
    raise Exception("[ERROR] - Exception in " + FILE_NAME + ": " + repr(e))