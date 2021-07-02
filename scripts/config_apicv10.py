import os, json
import utils
import api_calls

"""

API Connect v10 post install configuration steps --> https://www.ibm.com/docs/en/api-connect/10.0.x?topic=environment-cloud-manager-configuration-checklist

"""

FILE_NAME = "config_apicv10.py"
DEBUG = os.getenv('DEBUG','')

def info(step):
    return "[INFO]["+ FILE_NAME +"][STEP " + str(step) + "] - " 

try:

######################################################################################
# Step 1 - Get the IBM API Connect Toolkit credentials and environment configuration #
######################################################################################

    toolkit_credentials = utils.get_toolkit_credentials(os.environ["CONFIG_FILES_DIR"])
    environment_config = utils.get_env_config(os.environ["CONFIG_FILES_DIR"])
    if DEBUG:
        print(info(1) + "These are the IBM API Connect Toolkit Credentials")
        print(info(1) + "-------------------------------------------------")
        print(info(1), json.dumps(toolkit_credentials, indent=4, sort_keys=False))
        print(info(1) + "These is the environment configuration")
        print(info(1) + "--------------------------------------")
        print(info(1), json.dumps(environment_config, indent=4, sort_keys=False))

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
        print(info(2) + "This is the Bearer Token to work against the IBM API Connect Management endpoints")
        print(info(2) + "---------------------------------------------------------------------------------")
        print(info(2), admin_bearer_token)

#################################
# Step 3 - Get the Admin org ID #
#################################
    
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
        print(info(3) + "Admin Org ID: " + admin_org_id)

# ####################################
# # Step 4 - Create the Email Server #
# ####################################
    
#     url = 'https://' + environment_config["APIC_ADMIN_URL"] + '/api/orgs/' + admin_org_id + '/mail-servers'
    
#     # Create the data object
#     data = {}
#     data['title'] = 'Default Email Server'
#     data['name'] = 'default-email-server'
#     data['host'] = os.environ['EMAIL_HOST']
#     data['port'] = int(os.environ['EMAIL_PORT'])
#     credentials = {}
#     credentials['username'] = os.environ['EMAIL_USERNAME']
#     credentials['password'] = os.environ['EMAIL_PASSWORD']
#     data['credentials'] = credentials
#     data['tls_client_profile_url'] = None
#     data['secure'] = False

#     if DEBUG:
#         print(info(4) + "This is the data object:")
#         print(info(4), data)
#         print(info(4) + "This is the JSON dump:")
#         print(info(4), json.dumps(data))

#     response = api_calls.make_api_call(url, admin_bearer_token, 'post', data)

#     if response.status_code != 201:
#           raise Exception("Return code for creating the Email Server isn't 201. It is " + str(response.status_code))
#     email_server_url = response.json()['url']
#     if DEBUG:
#         print(info(4) + "Email Server url: " + email_server_url)

# ##################################################
# # Step 5 - Sender and Email Server Configuration #
# ##################################################

#     url = 'https://' + environment_config["APIC_ADMIN_URL"] + '/api/cloud/settings'
    
#     # Create the data object
#     # Ideally this would also be loaded from a sealed secret
#     data = {}
#     data['mail_server_url'] = email_server_url
#     email_sender = {}
#     email_sender['name'] = 'APIC Administrator'
#     email_sender['address'] = 'test@test.com'
#     data['email_sender'] = email_sender

#     if DEBUG:
#         print(info(5) + "This is the data object:")
#         print(info(5), data)
#         print(info(5) + "This is the JSON dump:")
#         print(info(5), json.dumps(data))

#     response = api_calls.make_api_call(url, admin_bearer_token, 'put', data)

#     if response.status_code != 200:
#           raise Exception("Return code for Sender and Email Server configuration isn't 200. It is " + str(response.status_code))

#######################################
# Step 6 - Register a Gateway Service #
#######################################

    # First, we need to get the Datapower API Gateway instances details

    url = 'https://' + environment_config["APIC_ADMIN_URL"] + '/api/cloud/integrations/gateway-service/datapower-api-gateway'

    response = api_calls.make_api_call(url, admin_bearer_token, 'get')

    if response.status_code != 200:
          raise Exception("Return code for getting the Datapower API Gateway instances details isn't 200. It is " + str(response.status_code))

    datapower_api_gateway_url = response.json()['url']
    if DEBUG:
        print(info(6) + "Email Server url: " + datapower_api_gateway_url)

    # Second, we need to get the TLS server profiles

    url = 'https://' + environment_config["APIC_ADMIN_URL"] + '/api/orgs/' + admin_org_id + '/tls-server-profiles'

    response = api_calls.make_api_call(url, admin_bearer_token, 'get')

    found = False
    tls_server_profile_url = ''
    if response.status_code != 200:
          raise Exception("Return code for getting the TLS server profiles isn't 200. It is " + str(response.status_code))
    for profile in response.json()['results']:
        if profile['name'] == "tls-server-profile-default":
            found = True
            tls_server_profile_url = profile['url']
    if not found:
        raise Exception("[ERROR] - The default TLS server profile was not found in the IBM API Connect Cluster instance")

    if DEBUG:
        print(info(6) + "Default TLS server profile url: " + tls_server_profile_url)

    # Third, we need to get the TLS client profiles

    url = 'https://' + environment_config["APIC_ADMIN_URL"] + '/api/orgs/' + admin_org_id + '/tls-client-profiles'

    response = api_calls.make_api_call(url, admin_bearer_token, 'get')

    found = False
    tls_client_profile_url = ''
    if response.status_code != 200:
          raise Exception("Return code for getting the TLS client profiles isn't 200. It is " + str(response.status_code))
    for profile in response.json()['results']:
        if profile['name'] == "gateway-management-client-default":
            found = True
            tls_client_profile_url = profile['url']
    if not found:
        raise Exception("[ERROR] - The Gateway Management TLS client profile was not found in the IBM API Connect Cluster instance")

    if DEBUG:
        print(info(6) + "Gateway Management TLS server profile url: " + tls_client_profile_url)


    # Finally, we can actually make the REST call to get the Default Gateway Service registered

    url = 'https://' + environment_config["APIC_ADMIN_URL"] + '/api/orgs/' + admin_org_id + '/availability-zones/availability-zone-default/gateway-services'
    
    # Create the data object
    data = {}
    data['name'] = "default-gateway-service"
    data['title'] = "Default Gateway Service"
    data['summary'] = "Default Gateway Service that comes out of the box with API Connect Cluster v10"
    data['endpoint'] = 'https://' + environment_config["APIC_GATEWAY_MANAGER_URL"]
    data['api_endpoint_base'] = 'https://' + environment_config["APIC_GATEWAY_URL"]
    data['tls_client_profile_url'] = tls_client_profile_url
    data['gateway_service_type'] = 'datapower-api-gateway'
    visibility = {}
    visibility['type'] = 'public'
    data['visibility'] = visibility
    sni = []
    sni_inner={}
    sni_inner['host'] = '*'
    sni_inner['tls_server_profile_url'] = tls_server_profile_url
    sni.append(sni_inner)
    data['sni'] = sni
    data['integration_url'] = datapower_api_gateway_url

    if DEBUG:
        print(info(6) + "This is the data object:")
        print(info(6), data)
        print(info(6) + "This is the JSON dump:")
        print(info(6), json.dumps(data))

    response = api_calls.make_api_call(url, admin_bearer_token, 'post', data)

    if response.status_code != 201:
          raise Exception("Return code for registering the Default Gateway Service isn't 201. It is " + str(response.status_code))

except Exception as e:
    raise Exception("[ERROR] - Exception in " + FILE_NAME + ": " + repr(e))