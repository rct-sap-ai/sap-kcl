from auto_sap.classes.auto_code_api_classes import auto_code_api

api = auto_code_api(dev = True)

api.post_timepoint(8, "Test Label")
api.post_timepoint(7, "Test Label2")