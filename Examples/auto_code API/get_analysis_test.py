from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator

dev_flag = False
api = AutoCodeAPI(dev=dev_flag)

trial_creator = TrialCreator(api, trial_id=20)

analyses = trial_creator.get_processed_analyses()
print("Processed analyses for trial 20:")
for row in analyses:
    print(row)
