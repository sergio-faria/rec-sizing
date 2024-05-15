from .ewh_flex import read_data
from .ewh_flex import ewh_preparation
import os


def ewh_varBackpack(paramsInput, dataset):

    # ##############################################
    # ##            Read Input Data               ##
    # ##############################################
    #
    # print(os.path.abspath(__file__))
    # # Input parameters JSON filepath
    # paramsInput_filePath = os.path.dirname(os.path.abspath(__file__)) + '\\data\\input\\input_parameters.json'
    # # User usage input JSON filepath (no load diagram)
    # dataset_filePath = os.path.dirname(os.path.abspath(__file__)) + '\\data\\input\\input_data.json'
    #
    # # Read data
    # dataset, paramsInput = read_data(paramsInput_filePath, dataset_filePath)

    ##############################################
    #             Data Preparation               #
    ##############################################

    # Select resample between 'no','15m','1h'
    varBackpack = ewh_preparation(paramsInput, dataset, resample='1h')

    return varBackpack
