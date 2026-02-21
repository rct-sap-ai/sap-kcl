from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
from auto_sap.classes.auto_code_classes import TimepointExtractor, VariableExtractor, AnalysisExtractor
from auto_sap.classes.chat_classes import OpenAIChat


dev_flag = True
run_design_vars = True
api = AutoCodeAPI(dev=dev_flag)

trials = api.get_(endpoint="trial")

trial_id = 17 if dev_flag else 20

if run_design_vars:
    trial_manager = TrialCreator(api, trial_id=trial_id)

    time_var = trial_manager.get_time_variable()
    print("get_time_variable output:", time_var)

    updated_time = trial_manager.update_time_variable(label="Timepoint", variable="time")
    print("update_time_variable response:", updated_time)

    design_vars = trial_manager.get_design_variables()
    print("get_design_variables output:", design_vars)


    design_var = trial_manager.update_design_variable(
        parameter="allocation",
        label="Treatment Group",
        variable="treatment_group"
    )   
    
    print("update_design_variable response:", design_var)
   