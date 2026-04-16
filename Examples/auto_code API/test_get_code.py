from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
from auto_sap.classes.auto_code_classes import TimepointExtractor, VariableExtractor, AnalysisExtractor
from auto_sap.classes.chat_classes import OpenAIChat


dev_flag = True
run_design_vars = True
api = AutoCodeAPI(dev=dev_flag)

trials = api.get_(endpoint="trial")

trial_id = 17 if dev_flag else 20

trial_manager = TrialCreator(api, trial_id=trial_id)


trial_manager.create_main_analysis_report()