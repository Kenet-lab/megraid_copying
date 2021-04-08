import os
import fnmatch
import smtplib
import logging
import io_helpers as i_o
from mne.io import read_info
from email.message import EmailMessage
from email.utils import formataddr as format_address

main_log = logging.getLogger(__name__) # get the log file created by megraid_main

def is_not_valid_subject(folder_name): # this should be a bit more sophisticated...
    """
    :param folder_name: string representing a subject's folder in MEGRAID
    :return: True (invalid), False (valid)
    """
    id = folder_name.split('_')[-1] # MEGRAID folders follow "subj_SUBJECTID" pattern
    return not id.isnumeric() and len(id) == 6 or 'AC' in id


def refine_search_by(subject_folder, dates, paradigms):
    """
    Filter subjects' raw files of interest by visit date and paradigm
    Loops through various visit folders first, filtering accordingly
    Then loops through matching visit folders, acquiring the names of raw data matching paradigms of interest
    :param subject_folder: path to subject's MEGRAID folder
    :param dates: list of strings representing dates to narrow the search (from megraid_config)
    :param paradigms: list of strings representing paradigms to narrow the search (from megraid_config)
    :return: dictionary of what the refined search has located
    """
    relevant_visits = [visit for visit in os.listdir(subject_folder) if ''.join(('20', visit[:2])) in dates]
    """ dictionary whose keys -> string of the visit date of interest and paradigm
                         whose values -> list of the paradigm data of interest
    """
    data_relevant_visits = {'_'.join((rel_visit, p)): fnmatch.filter(os.listdir(os.path.join(subject_folder, rel_visit)), f'*{p}*raw.fif')
                            for rel_visit in relevant_visits for p in paradigms}
    # return a dictionary with non-empty matches
    data_matches_relevant_visits = {visit_paradigm_pair:list_of_matches
                                    for visit_paradigm_pair, list_of_matches in data_relevant_visits.items() if list_of_matches}

    return data_matches_relevant_visits


def insert_visit_date_into_filename(raw_name, paradigm_visit_folder):
    """
    FIXATION FILE NAMING CONVENTION - the date of their respective visit is embedded into the raw filename
    :param raw_name: string representing the raw filename
    :param paradigm_visit_folder: string representing their visit's folder name
    :return: re-built raw filename, with the date of their visit now a part of it
    """
    filename_identifiers = raw_name.split('_') # create a list of key filename identifiers
    visit_folder_name = os.path.split(paradigm_visit_folder)[1] # infer the visit date from the visit folder name
    visit_yymmdd = visit_folder_name.split('_')[1]
    filename_identifiers.insert(-1, visit_yymmdd)  # insert the visit date into the list of filename identifiers
    return '_'.join(filename_identifiers) # re-build the filename


def prepare_to_copy_files(subject, meg_dir, subject_megraid_dir, visit_paradigm_pair, list_of_raws):
    """
    Build (if necessary) paradigm sub-directory for the subject, as well as a folder for storing their visit's data
    Also check if the current paradigm is fixation
    :param subject: string representing the subject ID
    :param meg_dir: string representing the path to the transcend/MEG directory
    :param subject_megraid_dir: string representing the path to the subject's MEGRAID directory
    :param visit_paradigm_pair: string denoting the visit date as MEGRAID stores it (YYMMDD)
    :param list_of_raws: list of strings for each raw file
    :return: MEGRAID visit folder path, subject's paradigm visit folder path, fixation = True/False
    """
    megraid_visit = visit_paradigm_pair.split('_')[0]
    megraid_visit_folder = os.path.join(subject_megraid_dir, megraid_visit)
    # read the measurement date from the .fif header
    measurement_date = i_o.read_measure_date(read_info(os.path.join(megraid_visit_folder, list_of_raws[0])))

    paradigm = visit_paradigm_pair.split('_')[1]
    paradigm_dir = os.path.join(meg_dir, paradigm)

    fixation = True if paradigm == 'fix' else False

    subject_paradigm_folder = os.path.join(paradigm_dir, subject)
    subject_paradigm_visit_folder = os.path.join(subject_paradigm_folder, f'visit_{measurement_date}')
    for subdir in [subject_paradigm_folder, subject_paradigm_visit_folder]:
        i_o.check_and_build_subdir(subdir)

    return megraid_visit_folder, subject_paradigm_visit_folder, fixation


def subject_id_does_match(subject, filename):
    """
    check whether the subject id in MEGRAID's subj_SUBJECTID subject folder matches
    the filenames in its visit subdirectory
    :return: True (the subject id matches), False (mismatch)
    """
    filename_identifiers = filename.split('_') # create a list of key filename identifiers
    subject_id_in_filename = filename_identifiers[0]
    return subject == subject_id_in_filename

def compose_and_send_email_update(log_file, date, recipient):
    """
    use the simple mail transfer protocol to attach the log file to an email
    :param log_file: string denoting the name of the log file created
    :param date: string denoting the current date
    :param recipient: string denoting the email address of whom to send the email to
    """
    message = EmailMessage()
    message['From'] = format_address(('SMTPD', 'noreply@localhost'))
    message['To'] = ', '.join(recipient) if len(recipient) > 1 else recipient
    message['Subject'] = f'MEGRAID copying update for code run on {date}'
    message.add_attachment(open(log_file, 'r').read(), filename=log_file)

    server = smtplib.SMTP('localhost')
    server.send_message(message)
    server.quit()
    return
