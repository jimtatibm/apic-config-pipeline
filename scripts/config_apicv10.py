import os, json
import utils

"""

API Connect v10 post install configuration steps --> https://www.ibm.com/docs/en/api-connect/10.0.x?topic=environment-cloud-manager-configuration-checklist

"""

FILE_NAME = "config_apicv10.py"
INFO = "[INFO]["+ FILE_NAME +"] - " 

try:

########################################################
# Step 1 - Get the IBM API Connect Toolkit credentials #
########################################################

    toolkit_credentials = utils.get_toolkit_credentials(os.environ["CONFIG_FILES_DIR"])


###############################################################
# Step 2 - Get the IBM API Connect Cloud Manager Bearer Token #
###############################################################

    bearer_token_response = utils.get_bearer_token(os.environ["APIC_ADMIN_URL"],
                                                    "admin",
                                                    os.environ["APIC_ADMIN_PASSWORD"],
                                                    "admin/default-idp-1",
                                                    toolkit_credentials["toolkit"]["client_id"],
                                                    toolkit_credentials["toolkit"]["client_secret"])

    print("YYYYYYYYYYYYYYYYYYYYYY")
    print("This is the Bearer Token", bearer_token_response['access_token'])
except Exception as e:
    raise Exception("[ERROR] - Exception in " + FILE_NAME + ": " + repr(e))