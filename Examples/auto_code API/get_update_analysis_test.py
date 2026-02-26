from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
from auto_sap.classes.auto_code_classes import TimepointExtractor, VariableExtractor, AnalysisExtractor
from auto_sap.classes.chat_classes import OpenAIChat


dev_flag = True
run_analysis = True
update_analysis = True
api = AutoCodeAPI(dev=dev_flag)

chat_bot = OpenAIChat(model_name="gpt-5-nano")
analysis_extractor = AnalysisExtractor(chat_bot=chat_bot)

trials = api.get_(endpoint="trial")

trial_id = 17 if dev_flag else 20


if run_analysis:
    trial_creator = TrialCreator(api, trial_id=trial_id)

    analysis_list2 = trial_creator.get_processed_analyses()


    print(f"\n \n ANALYSIS LIST: {analysis_list2}")


    methods = api.get_(endpoint = "method")
    method_ids = set()
    for method in methods:
        method_ids.add(method["id"])

    args = trial_creator.get_analysis_validator_args()
    outcome_list = args["outcomes"]
    method_ids = args["allowed_method_ids"]

    errors, warnings = analysis_extractor.validate(
        analysis_list=analysis_list2, 
        outcomes=outcome_list, 
        allowed_method_ids=method_ids)
    print(f"errors: {errors}")
    print(f"warnings: {warnings}")

    # print(f"Processed analyses for trial : {trial_id}")
    # for row in analysis_list:
    #     print(row)

if update_analysis:
    updated_analysis = trial_creator.update_analyses(analysis_list2)

    print("Updated analyses response:", updated_analysis)


    # Expected analysis schema:
    # "outcome_variable": "phq9_total",
    # "timepoints": [2],
    # "method": "method_id_from_list"

#TODO: Get update analysis working. Move all this into methods. Run from streamlit.
