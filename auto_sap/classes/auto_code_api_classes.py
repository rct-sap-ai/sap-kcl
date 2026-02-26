import requests
import os
import dotenv

dotenv.load_dotenv()

class AutoCodeAPI:
    def __init__(self, token=None, dev=False):
        # Determine the URL
        self.api_url = "http://127.0.0.1:8000/api/" if dev else "https://www.statsplan.com/api/"
        
        # 1. Use the passed token 
        # 2. If None, fall back to the correct environment variable
        if token:
            self.TOKEN = token
        else:
            env_key = "AUTOCODE_API_TOKEN_DEV" if dev else "AUTOCODE_API_TOKEN_PROD"
            self.TOKEN = os.getenv(env_key)

        # Throw a clear error if no token was found anywhere
        if not self.TOKEN:
            raise ValueError(f"API Token not found. Please provide it or set {env_key}")

        self.headers = {
            "Authorization": f"Token {self.TOKEN}",
            "Content-Type": "application/json"
        }


    def post_(self, data, endpoint: str):
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status() 

        if response.content:
            return response.json()
        return None
    
    def post_file(self, data, endpoint: str):
        """Download a file from a POST endpoint and return binary content."""
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.content


    def get_(self, endpoint: str, params: dict = None):
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def patch_(self, endpoint: str, data: dict):
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}" +"/"
        response = requests.patch(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def put_(self, endpoint: str, data: dict):
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}" +"/"
        response = requests.put(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
   
    def get_methods(self):
        response = self.get_("method/")
        return response
    
    def get_variable_type_id(self, title):
        variable_types = self.get_("variable_type/")    
        for vt in variable_types:
            if vt['title'] == title:
                return vt['id']
        raise LookupError(f"Variable type with title '{title}' not found.")
    
    def get_sap_json(self, trial_id):
        sap_json = self.get_(endpoint = f"sap_json/latest/?trial={trial_id}")
        return sap_json['sap_json']


class TrialCreator:
    def __init__(self, api_instance, acronym: str = "", title: str = "", trial_id: int = None):
        self.api = api_instance

        if trial_id:
            print(f"Using provided trial ID: {trial_id}")
            self.trial_id = trial_id
            return
        else:
            print(f"Looking for existing trial with acronym '{acronym}' and title '{title}'...")
            trial_data = self.api.get_("trial/", params = {"acronym": acronym, "title": title})

            trial_id = trial_data[0]['id'] if trial_data != [] else None
            if trial_id == None:
                print("Creating new trial...")
                trial_data = self.api.post_(
                    data = {
                        "acronym": acronym,
                        "title": title
                    },
                    endpoint = "trial/"
                )
                self.trial_id = trial_data['id']
            else:
                print("Using existing trial...")
                self.trial_id = trial_id
    
        
    def patch_trial(self, new_data):
        response = self.api.patch_(endpoint = f"trial/{self.trial_id}", data =   new_data)
        return response

    def get_sap_json(self):
        sap_json = self.api.get_sap_json(self.trial_id)
        return sap_json['sap_json']
    
    def add_sap_json(self, sap_json):


        data = {
            "sap_json": sap_json,
            "trial": self.trial_id
        }

        print("Adding SAP JSON to trial...")
        print(data)

        response = self.api.post_(endpoint = "sap_json/", data = data)
        return response
    
    def get_time_variable(self):
        trial_data = self.api.get_(endpoint = f"trial/{self.trial_id}")
        time_variable_id = trial_data.get('time_variable', None)
        if time_variable_id is None:
            print("No time variable set for this trial.")
            return None
        time_variable_data = self.api.get_(endpoint = f"measure/{time_variable_id}")
        return time_variable_data
    
    def update_time_variable(self, label: str, variable: str):
        """
        Create or update the time variable for this trial.

        Args:
            label: Human-readable label for the time variable
            variable: Short variable name (e.g., 'timepoint')
        """
        # Get the Categorical variable type ID

        # Create the measure data
        measure_data = {
            "label": label,
            "variable": variable,
            "variable_type": "Categorical"
        }

        # Add the measure (no value_labels needed for time variable)
        time_var_measure = self.add_measure(measure_data, value_labels=None)

        # Update the trial's time_variable field
        self.patch_trial(new_data={"time_variable": time_var_measure['id']})

        return time_var_measure

    def update_timepoints(self, timepoint_list):
        timepoint_ids = []
        for tp in timepoint_list:
            response = self.api.post_(endpoint = "timepoint/", data = tp)
            timepoint_ids.append(response['id'])
        self.timepoint_ids = timepoint_ids

        self.patch_trial(new_data = { "timepoints": self.timepoint_ids})


        return timepoint_ids
    
    def get_design_variables(self):
        design_variables = self.api.get_(f"design_variable/?trial={self.trial_id}")
        enriched_design_vars = []
        for dv in design_variables:
            variable_id = dv['variable']
            measure_data = self.api.get_(endpoint=f"measure/{variable_id}")
            measure_data['parameter'] = dv['parameter']
            enriched_design_vars.append(measure_data)
        return enriched_design_vars

    def update_design_variable(self, parameter: str, label: str, variable: str):
        """
        Create or update a design variable for this trial.

        Args:
            parameter: Design parameter slug (e.g., 'allocation', 'centre')
            label: Human-readable label for the variable
            variable: Short variable name (e.g., 'treatment_group', 'site')
        """
        # Create the measure data (Categorical type)
        measure_data = {
            "label": label,
            "variable": variable,
            "variable_type": "Categorical"
        }

        # Add the measure (no value_labels needed)
        design_var_measure = self.add_measure(measure_data, value_labels=None)

        # Post to design_variable endpoint
        design_var_data = {
            "trial": self.trial_id,
            "parameter": parameter,  # slug field
            "variable": design_var_measure['id']  # measure ID
        }

        response = self.api.post_(endpoint="design_variable/", data=design_var_data)

        return response
    
    def add_measure(self, variable_data, value_labels = None):
        if value_labels is not None:
            value_label_ids = []
            for label in value_labels:
                print("Posting value label:", label)
                value_label =self.api.post_(endpoint = "value_label/", data = label)
                value_label_ids.append(value_label['id'])
            variable_data['value_labels'] = value_label_ids


        variable_type_id = self.api.get_variable_type_id(variable_data['variable_type'])
        variable_data['variable_type'] = variable_type_id
        variable_data['value_labels'] = value_label_ids if value_labels is not None else []

        measure = self.api.post_(endpoint = "measure/", data = variable_data)
        
        return measure
    
    def update_timevar(self, variable_data, value_labels):
        self.update_timepoints(value_labels)
        timevar = self.add_measure(variable_data, value_labels)
        self.time_variable_id = timevar['id']
        new_data = {
            "time_variable": self.time_variable_id,
        }
        self.patch_trial(new_data = new_data)
        return timevar
    
    def update_allocation_variable(self, variable_data, value_labels):
        allocation_var = "Method not yet implemented"
        print("Allocation variable update not yet implemented.")
        
        # allocation_var = self.add_measure(variable_data, value_labels)
        # self.allocation_variable_id = allocation_var['id']
        # new_data = {
        #     "allocation_variable": self.allocation_variable_id,
        # }
        # self.patch_trial(new_data = new_data)
        return allocation_var
    
    def update_design_variables(self, design_variable_list):
        
        design_variable_ids = []
        for dv in design_variable_list:
            variable_data = {
                "variable": dv['variable'],
                "label": dv['label'],
                "variable_type": "Binary"
            }
            measure_response = self.add_measure(variable_data, value_labels = None)
            measure_id = measure_response['id']
            
            dv_data = {
                "variable": measure_id,
                "parameter": dv['design_parameter'],
                "trial": self.trial_id,
            }
            response = self.api.post_(endpoint = "design_variable/", data = dv_data)
            print("Posted design variable:", response)
            design_variable_ids.append(response['id'])
        self.design_variable_ids = design_variable_ids

        return design_variable_ids
    
    def get_allocation_groups(self):
        response = self.api.get_(endpoint = f"allocation_group/?trials={self.trial_id}")
        return response

    def update_allocation_groups(self, allocation_group_list):
        cleaned_list = []
        for ag in allocation_group_list:
            if 'value' not in ag or 'label' not in ag:
                raise ValueError("Each allocation group must have 'value' and 'label' keys.")
            cleaned_list.append({
                "value": ag['value'],
                "label": ag['label']
            })


        response = self.patch_trial(new_data = {"allocation_groups": cleaned_list})

        return response

  


    def get_timepoints(self):
        # Fetch the single trial object
        trial_data = self.api.get_(endpoint = f"trial/{self.trial_id}")
        timepoint_ids = trial_data.get('timepoints', [])
        tp_data_list = []
        for tp_id in timepoint_ids:
            tp_data = self.api.get_(endpoint = f"timepoint/{tp_id}")
            tp_data_list.append(tp_data)
        return tp_data_list
    
    def get_outcome_variables(self):
        outcome_vars = self.api.get_("outcome_variable/", params = {"trial": self.trial_id})
        return outcome_vars
    

    def extract_measure_fields(self, measures: list) -> list[dict]:
        """Extract key fields from measures list, grouped by variable with all timepoints collected."""
        variable_types = self.api.get_("variable_type/")
        grouped = {}
        for m in measures:
            outcome = m["outcome"]
            var = outcome["variable"]
            tp_value = m["timepoint"]["value"]

            if var not in grouped:
                grouped[var] = {
                    "label": outcome["label"],
                    "variable": var,
                    "variable_type": next((item['title'] for item in variable_types if item['id'] == outcome['variable_type']), None),
                    "timepoints": [],
                }
            grouped[var]["timepoints"].append(tp_value)



        return list(grouped.values())
    
    def get_processed_measures(self):
        measures = self.get_outcome_variables()
        processed_measures = self.extract_measure_fields(measures)
        return processed_measures
    
    #outcomes list is a list of dicts with keys: label, variable, variable_type, timepoints


    def update_outcomes(self, outcome_list):
        outcome_variable_list = []
        for outcome in outcome_list:
            measure_data = {
                "label": outcome['label'],
                "variable": outcome['variable'],
                "variable_type": outcome['variable_type']
            }
            value_labels = outcome.get('value_labels', None)

            measure_response = self.add_measure(measure_data, value_labels)
            measure_id = measure_response['id']
            timepoint_list = self.get_timepoints()
        
            for tp in outcome['timepoints']:
                print("checking tp dict for value:", tp)
                print("available timepoints:", timepoint_list)
                tp_dict = next((item for item in timepoint_list if item.get('value') == tp), None)
                print("found tp dict:", tp_dict)
                tp_id = tp_dict['id']
                outcome_variable_list.append({
                    "outcome": measure_id,
                    "timepoint": tp_id,
                })

        updated_outcomes = self.api.put_(endpoint = f"trial/{self.trial_id}/set-outcome-variables", data = outcome_variable_list)

        return updated_outcomes
    

    def get_outcome_variable_id_from_outcome_label_timepoint(self, analysis, measures_list, timepoint_list, outcome_variable_list):
        outcome_variable = analysis['outcome_variable']
        timepoint_value = analysis['timepoint']

        measure = next((item for item in measures_list if item.get('variable') == outcome_variable), None)
        if measure is None:
            raise LookupError("Cannot find measure with variable:", outcome_variable)
        measure_id = measure['id']
        
        tp_dict = next((item for item in timepoint_list if item.get('value') == timepoint_value), None)
        if tp_dict is None:
            raise LookupError("Cannot find timepoint with label:", timepoint_value)
        tp_id = tp_dict['id']


        outcome_variable = next((item for item in outcome_variable_list if item.get('outcome') == measure_id and item.get('timepoint') == tp_id), None)
        if outcome_variable is None:
            raise LookupError(f"Cannot find outcome variable for {outcome_variable} at {timepoint_value}. Check that this outcome is measured a the specified timepoint.")
        outcome_variable_id = outcome_variable['id']
        
        return {'outcome_variable_id': outcome_variable_id, 'measure_id': measure_id, 'timepoint_id': tp_id}


    def extract_processed_analysis(self, analyses: list) -> list[dict]:
        """Extract key fields from analyses list with timepoints as a list of values."""
        analysis_list = []
        for analysis in analyses:
            # timepoints is now M2M, so it's a list of timepoint objects
            timepoints = analysis.get("timepoints", [])
            timepoint_values = [tp["value"] for tp in timepoints] if isinstance(timepoints, list) else []

            covariates = analysis.get("covariates", [])
            covariate_variables = [c["variable"] for c in covariates] if isinstance(covariates, list) else []

            analysis_list.append({
                "method": analysis["method"],
                "outcome_variable": analysis["outcome"]["variable"],
                "timepoints": timepoint_values,
                "covariates": covariate_variables,
            })
        return analysis_list
        
    
    def get_processed_analyses(self):
        raw_analyses = self.api.get_(endpoint = f"analysis/?trial={self.trial_id}")
        processed_analyses = self.extract_processed_analysis(raw_analyses)
        return processed_analyses

    def get_analysis_validator_args(self):
        methods = self.api.get_(endpoint = "method")
        method_ids = set()
        for method in methods:
            method_ids.add(method["id"])

        outcome_list = self.get_processed_measures()
        return {
            "allowed_method_ids": method_ids,
            "outcomes": outcome_list
        }



    def update_analyses(self, analysis_list):
        timepoint_list = self.get_timepoints()
        measures_list = self.api.get_(endpoint = "measure/")

        order = 0
        analysis_data_list = []
        for analysis in analysis_list:
            measure_item = next((item for item in measures_list if item.get('variable') == analysis['outcome_variable']), None)
            measure_id = measure_item['id'] if measure_item else None

            # timepoints is now a list, map each value to its ID
            timepoint_values = analysis.get('timepoints', [])
            timepoint_ids = []
            for tp_value in timepoint_values:
                tp = next((item for item in timepoint_list if item.get('value') == tp_value), None)
                if tp:
                    timepoint_ids.append(tp['id'])

            covariate_vars = analysis.get("covariates", [])

            analysis_data_list.append({
                "outcome": measure_id,
                "timepoints": timepoint_ids,
                "method": analysis['method'],
                "order": order,
                "covariates": covariate_vars,
            })
        response = self.api.put_(endpoint = f"trial/{self.trial_id}/set-analyses", data = analysis_data_list)
        return response
    


    def get_trial_details(self):
        trial_data = self.api.get_(endpoint = f"trial/{self.trial_id}", params = {"expand": "true"})
        return trial_data
    
    def create_main_analysis_report(self):
        print("Creating main analysis report...")
        response = self.api.post_(endpoint = f"trial/{self.trial_id}/create_main_analysis_report/", data = {})
        return response
    
    def get_code_for_main_analysis(self):
        print("Fetching code for main analysis report...")
        response = self.api.post_file(
            endpoint = f"trial/{self.trial_id}/get_code_for_report/", 
            data = {'report_title': 'Main Analysis'})
        return response
    

def get_sap_code_from_json(code_json, dev_flag = True):

    # To do, replace defaults with inputs from streamlit app.
    print("\n Extracting timepoints from autocode JSON...") 
    timepoint_value_labels = code_json.get("timepoints", [])
    print(timepoint_value_labels)

    print("\n Extracting outcomes from autocode JSON...")
    


    outcomes = code_json.get("variables", [])
    print(outcomes)
    # analyses_list = code_json.get("analyses", [])


    aconym = "STEAMTrial"
    title = "Streamlit Trial Example"

    design_variables = [
        {'design_parameter': "allocation", 'variable':"treatment_group", 'label': "Treatment Group"},
        #{'design_parameter': "centre", 'variable':"site", 'label': "Site"}, uncomment for multicentre example
    ]

    allocation_groups = [
        {"value": 0, "label": "Control"},
        {"value": 1, "label": "Intervention"},
    ]

    time_var = {'variable': 'timepoint', 'label': 'Timepoint', 'variable_type': 'Categorical'}
  
  
    descriptive_method_id = 1
    if dev_flag:
        descriptive_method_id = 1  # In DEV, the IDs may differ
    linear_model_method_id = 2
    if dev_flag:
        linear_model_method_id = 3  # In DEV, the IDs may differ

    analyses_list = [
            {
                "outcome_variable": "depression",
                "timepoint": "0",
                "method": descriptive_method_id,
                "table": "baseline"
            },  {
                "outcome_variable": "anxiety",
                "timepoint": "0",
                "method": descriptive_method_id,
                "table": "baseline"
            },
            {
                "outcome_variable": "depression",
                "timepoint": "1",
                "method": linear_model_method_id,
                "table": "main_analysis"
            },
                    {
                "outcome_variable": "anxiety",
                "timepoint": "2",
                "method": linear_model_method_id,
                "table": "main_analysis"
            }
        ]


    """Given a SAP autocode JSON, fetch the generated code as a zip file."""
    api = AutoCodeAPI(dev=dev_flag)

    # Creating the trial 
    trial_manager = TrialCreator(api, acronym = aconym, title = title)

    # Sending data
    trial_manager.update_timevar(variable_data = time_var, value_labels = timepoint_value_labels)
    trial_manager.update_allocation_groups(allocation_group_list = allocation_groups)
    trial_manager.update_design_variables(design_variables)
    trial_manager.update_outcomes(outcomes)
    trial_manager.add_analyses(analyses_list)
    report_response = trial_manager.create_main_analysis_report()
    print(report_response)
    code_zip_file = trial_manager.get_code_for_main_analysis()

   
    return code_zip_file

