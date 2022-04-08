import mne
import fnmatch
import logging
import numpy as np
from os.path import join, isdir, isfile
from os import mkdir, listdir


def find_file_matches(loc, pattern):
    """
    :param loc: string denoting where file(s) may be found
    :param pattern: string to identify file(s) specified by it
    :return: list of file(s) found matching a given pattern, in a given location
    """
    files_matching_pattern = fnmatch.filter(listdir(loc), pattern)
    file_matches = [] if len(files_matching_pattern) == 0 else files_matching_pattern
    logging.info(f'The following {len(file_matches)} were found matching the pattern {pattern} in {loc}:\n{listdir(loc)}')
    return file_matches


def preload_raws(loc, pattern):
    """
    :param loc: string denoting where raw file(s) may be found
    :param pattern: string to identify, match the correct file(s)
    :param concat: boolean keyword argument to turn on/off raw file concatenation (default True)
    :return: pre-loaded raw .fif file(s)
    """
    list_of_raws = find_file_matches(loc, pattern)
    try:
        raws = [mne.io.read_raw_fif(join(loc, fif), preload=True) for fif in list_of_raws]
    except TypeError:
        logging.info('Raw files failed to be read')
    return raws


def get_subject_id_from_data(data):
    """
    :param data: MNE object like raw, epochs, tfr,... that has an Info attribute
    :return: string denoting the subject ID
    """
    return data.info['subject_info']['his_id']



def read_measure_date(info):
    """
    read measure date, convert to YYYYMMDD to find matching ERM file
    :param info: MNE info object
    :return: date (YYYYMMDD)
    """
    try:
        visit_datetime = info['meas_date']
    except KeyError:
        logging.info('Unable to parse measure timestamp from Info')
    return visit_datetime.strftime('%Y%m%d')


def get_measure_date_from_path(path, pattern):
    """
    :param path: string denoting the path to the file that we will read the information header from
    :param pattern: string denoting the file's name that we wish to read information from
    :return: visit date as a string (YYYYMMDD)
    """
    info_files = find_file_matches(path, pattern)
    info = mne.io.read_info(join(path, info_files[0]), verbose=False)
    return read_measure_date(info)



def check_and_build_subdir(subdir): # needs work?
    """
    build subject-specific subdirectories
    :param subdir: subject specific subdirectory name
    """
    if not isdir(subdir):
        mkdir(subdir)
        logging.info(f'{subdir} created')


def format_variable_names(replace_dict, *vars):
    """ format any number of variable names
    :param replace_dict: dictionary whose keys are values to replace and values are replacement values
    :param vars: any number of strings that we would like to replace values of"""
    return_list = [None] * len(vars)
    for i, var in enumerate(vars):
        for key, value in replace_dict.items():
            if key in var:
                var = var.replace(key, value)
            else:
                continue
        return_list[i] = var
    if len(vars) == 1: # return types should be identical, needs improvement ****
        return return_list[0]
    else:
        return tuple(return_list)

