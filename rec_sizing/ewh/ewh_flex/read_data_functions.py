##############################################
##           Read Data Functions            ##
##############################################

import pandas as pd
import json

def read_data(paramsInput_filePath, dataset_filePath):
    # required data from user (prompted)
    with open(paramsInput_filePath) as json_data:
        paramsInput = json.load(json_data)

    if paramsInput['load_diagram_exists'] == 1:
        try:
            # read load diagram JSON
            dataset = pd.read_json(dataset_filePath, convert_dates=False)
        except:
            # read load diagram CSV
            dataset = pd.read_csv(dataset_filePath)
        # rename the two column
        dataset.columns = ['timestamp', 'load']
        # convert to datetime
        try:
            dataset['timestamp'] = pd.to_datetime(dataset['timestamp'], utc=True)
        except:
            dataset['timestamp'] = pd.to_datetime(dataset['timestamp'], dayfirst=True, utc=True)
    else:
        # read input water usage calendar
        with open(dataset_filePath) as json_data:
            dataset = json.load(json_data)

    ## verify minute resolution and missing data
    dataset = verify_1min_resolution(dataset)

    return dataset, paramsInput


def gui_data(guiBackpack):
    print(guiBackpack)
    ### dataset
    if guiBackpack['load_diagram_exists'] == 1:
        if guiBackpack['file_type'] == 'json':
            dataset = pd.read_json(guiBackpack['dataset'], convert_dates=False)
        else:
            dataset = pd.read_csv(guiBackpack['dataset'])
        # rename the two column
        dataset.columns = ['timestamp', 'load']
        # convert to datetime
        try:
            dataset['timestamp'] = pd.to_datetime(dataset['timestamp'], utc=True)
        except:
            dataset['timestamp'] = pd.to_datetime(dataset['timestamp'], dayfirst=True, utc=True)

        ## verify minute resolution and missing data
        dataset = verify_1min_resolution(dataset)

    else:
        dataset = pd.DataFrame({'start': [], 'duration': []})
        for row in range(guiBackpack['num_rows']):
            _start = pd.to_datetime(guiBackpack['session_state'][f'start_{row}'])
            _duration = guiBackpack['session_state'][f'duration_{row}']
            dataset.loc[len(dataset)] = [_start, _duration]
            del _start, _duration

    ### input params
    paramsInput = {
        "user": "sample_user",
        "datetime_start": "2022-12-07T00:00:00.000Z",
        "datetime_end": "2022-12-13T23:59:00.000Z",
        "load_diagram_exists": guiBackpack['load_diagram_exists'],
        "ewh_specs": {
            "ewh_capacity": guiBackpack['ewh_capacity'],
            "ewh_power": guiBackpack['ewh_power'],
            "ewh_max_temp": guiBackpack['ewh_max_temp'],
            "user_comf_temp": guiBackpack['user_comf_temp'],
            "tariff": guiBackpack['tariff'],
            "price_simple": guiBackpack['price_simple'],
            "price_dual_day": guiBackpack['price_dual_day'],
            "price_dual_night": guiBackpack['price_dual_night'],
            "tariff_simple": guiBackpack['tariff_simple'],
            "tariff_dual": guiBackpack['tariff_dual']
        }
    }

    return dataset, paramsInput


def verify_1min_resolution(dataset):
    ## creates template from start and finish timestamps with minute resolution
    ## by joining the original dataset with this template, assures that all instances
    ## exists inside the final dataset. Missing values are fixed with 0.

    df = dataset.copy()
    # order by datetime
    df = df.sort_values(by='timestamp', ascending=True).reset_index(drop=True)
    # extract start date
    _start = df['timestamp'].iloc[0].strftime('%Y-%m-%d')
    # extract end date
    _end = df['timestamp'].iloc[-1].strftime('%Y-%m-%d 23:59')
    # create full length template, with 1-min res.
    _template = pd.DataFrame(pd.date_range(_start, _end, freq='min', tz='UTC'), columns=['timestamp'])
    # resample the original dataset to 1-min
    df = df.resample('1min', on='timestamp').sum().reset_index()
    # merge to the template
    df = _template.merge(df, how='left', left_on='timestamp', right_on='timestamp')

    return df
