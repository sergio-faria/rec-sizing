##############################################
#            Read Data Functions             #
##############################################

import pandas as pd
import json


def read_data(paramsInput_filePath, dataset_filePath):
    # required data from user (prompted)
    with open(paramsInput_filePath) as json_data:
        paramsInput = json.load(json_data)

    if paramsInput['load_diagram_exists'] == 1:
        # read load diagram JSON
        dataset = pd.read_json(dataset_filePath, convert_dates=False)
        # rename the two column
        dataset.columns = ['timestamp', 'load']
        # convert to datetime
        dataset['timestamp'] = pd.to_datetime(dataset['timestamp'], dayfirst=True, utc=True)
    else:
        # read input water usage calendar
        with open(dataset_filePath) as json_data:
            dataset = json.load(json_data)

    return dataset, paramsInput
