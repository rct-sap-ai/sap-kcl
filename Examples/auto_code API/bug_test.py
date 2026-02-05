from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator


#set up connection to auto_code API. Only set dev = True if you have access to a local development server.
# The API class looks for an environment variable named AUTOCODE_API_TOKEN_DEV or AUTOCODE_API_TOKEN_PROD. This can be passed using the 'token' argument if preferred.

dev_flag = False
api = AutoCodeAPI(dev = dev_flag)

trial_21 = api.get_("trial/21/")

print(trial_21)

