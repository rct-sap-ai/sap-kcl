from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator
from datetime import datetime


#set up connection to auto_code API. Only set dev = True if you have access to a local development server.
# The API class looks for an environment variable named AUTOCODE_API_TOKEN_DEV or AUTOCODE_API_TOKEN_PROD. This can be passed using the 'token' argument if preferred.

dev_flag = False
api = AutoCodeAPI(dev = dev_flag)


# Inputs:
acronym = "API_Long_Title_Test"
title = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam luctus vulputate pretium. Duis finibus, augue vel convallis imperdiet, dui urna maximus arcu, ac iaculis sapien libero vel dolor. Donec purus ante, malesuada eu lacus non, interdum hendrerit nibh. Nullam et mi feugiat est tempor bibendum. Ut tristique nulla suscipit venenatis sollicitudin. Nam eu orci et erat iaculis pellentesque ut et arcu. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nulla luctus leo orci, at pellentesque velit fringilla ut. Sed tincidunt urna ac mi scelerisque sodales. Nullam pulvinar id mauris eget cursus. Donec et risus et urna mattis scelerisque. Phasellus ornare sodales lacus, sed accumsan elit laoreet vitae. Etiam finibus vitae justo vel pretium. Nunc mollis id nisi vel volutpat. Curabitur viverra orci non libero iaculis bibendum. Nunc sed cursus risus. Sed non mauris vel ipsum congue posuere. Sed cursus nibh a diam blandit tempus. Integer sagittis, est ut gravida placerat, ante nunc suscipit ante, non gravida dui neque ac mi. Proin nunc sem, lobortis sed iaculis quis, elementum id urna. Sed scelerisque tempor dolor a tincidunt. Morbi accumsan sed justo non aliquam. Interdum et malesuada fames ac ante ipsum primis in faucibus. Donec augue mauris."

trial_creator = TrialCreator(api, acronym, title)
