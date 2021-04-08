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


def find_events(raw, stim_channel):
    """
    :param raw: raw file whose info to parse
    :param stim_channel: string stimulus channel name
    :return: events
    :return: events baseline
    """
    events = mne.find_events(raw, stim_channel=stim_channel, shortest_event=1)
    # shortest event -> the minimum number of samples an event must last
    events_differential_corrected = differentiate_superimposed_events(events)
    return events, events_differential_corrected


def differentiate_superimposed_events(events, value=0):
    """
    set the baseline of the trigger channel to a specified value
    :param events: mne Events
    :param value: value to set baseline events to (usually zero)
    :return: events baseline
    """
    events_baseline = events.copy()
    events_baseline[:, 2] = events[:, 2] - events[:, 1]
    events_baseline[:, 1] = np.zeros(len(events[:, 1])) + value
    events_differential_corrected = events_baseline
    return events_differential_corrected


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


def read_proj(proj_loc, proj_fname): # could certainly eliminate this function, call explicitly where needed
    """
    :param kind: SSP projection channel kind (EOG, ECG)
    """
    return mne.read_proj(join(proj_loc, proj_fname))


def save_proj(projs, proj_save_loc, proj_fname, kind):
    """
    :param kind: SSP projection channel kind (EOG, ECG)
    """
    proj_save_name = format_variable_names({'kind': kind}, proj_fname)
    mne.write_proj(join(proj_save_loc, proj_save_name), projs)


def check_and_build_subdir(subdir): # needs work?
    """
    build subject-specific subdirectories
    :param subdir: subject specific subdirectory name
    """
    if not isdir(subdir):
        mkdir(subdir)
        logging.info(f'{subdir} created')


def save_bad_channels(raw, bads, save_loc, save_name):
    with open(join(save_loc, save_name), 'a+') as bads_file:
        if isfile(bads_file):
            current_bads = [line.strip() for line in bads_file.readlines()]
            bads_to_add = list(set(bads).difference(set(current_bads)))  # check if any of the "new" bads were already saved
            bads_file.write(raw)
            for bad_to_add in bads_to_add:
                bads_file.write(f'{bad_to_add}\n')
            bads_file.close()
        else:
            bads_file.write(raw)
            for bad in bads:
                bads_file.write(f'{bad}\n')
            bads_file.close()
    return bads


def save_epochs(epochs, condition_name, save_loc, epoch_pattern, overwrite=True):
    """save epoch files"""
    epoch_fname = format_variable_names({'condition': condition_name}, epoch_pattern)
    epochs.save(join(save_loc, epoch_fname), overwrite=overwrite)


def read_bad_channels_eeg(loc, eeg_bads_fname):
    eeg_bads_txt = open(join(loc, eeg_bads_fname))
    lines = eeg_bads_txt.readlines()
    eeg_bads = [line.strip() for line in lines]
    return eeg_bads


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


def log_projs(projs, kind): # logging function for SSP projection information
    if projs: # projections were found and added
        logging.info(f'Projections ({kind}) found:\n{projs}')
    else: # no projections found or added
        logging.info(f'No {kind} projections added or found')


def log_epochs(epochs): # logging function for epoch data information
    logging.info(f'General epoch information:\n{epochs}')
    logging.info(f'Detailed view:\n{epochs.info}') # look into epochs.drop_log?


