from auto_sap.classes.auto_code_api_classes import auto_code_api

api_prod = auto_code_api()

api_prod.post_timepoint(8, "Test Label")
api_prod.post_timepoint(7, "Test Label2")