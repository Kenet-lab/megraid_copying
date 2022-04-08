import os
import shutil
import logging
import megraid_config as mgr_cfg
import megraid_functions as mgr_fcn

# run by typing: %run megraid_main

def copy_files_if_needed_and_check(raws, subject, subject_megraid_visit_folder, subject_paradigm_visit_folder, fixation):
    """
    Copy files from MEGRAID to a subject's paradigm/visit_YYYYMMDD folder in transcend/MEG
    :param fixation: True/False denoting whether the paradigm we are planning on copying is fixation
    """
    logging.info(f'{subject} has {len(raws)} in their MEGRAID visit folder')
    for raw in raws:
        # counter is insurance for unforeseen failures, increment the counter for each case the raw is accounted for
        did_we_catch_the_file_tracker = 0
        source_file = os.path.join(subject_megraid_visit_folder, raw)  # MEGRAID file path

        raw = mgr_fcn.insert_visit_date_into_filename(raw, subject_paradigm_visit_folder) if fixation else raw

        dest_file = os.path.join(subject_paradigm_visit_folder, raw)  # transcend file path

        if not mgr_fcn.subject_id_does_match(subject, raw): # mention which file is not being copied, because of typo
            err_msg_typo = f'There exists a typo between {subject} and one of its filenames: {raw}\n'
            logging.error(err_msg_typo)
            print(err_msg_typo)
            did_we_catch_the_file_tracker += 1
            continue
        elif not os.path.isfile(dest_file): # copy the file and log the file being copied
            info_msg_copying = f'Copying {source_file} to {dest_file} for {subject}\n'
            logging.info(info_msg_copying)
            print(info_msg_copying)
            shutil.copyfile(source_file, dest_file)
            did_we_catch_the_file_tracker += 1
        elif os.path.isfile(dest_file):
            info_msg_already_exists = f'Tried copying {source_file} to {dest_file} for {subject}, but it already exists!\n'
            logging.info(info_msg_already_exists)
            print(info_msg_already_exists)
            did_we_catch_the_file_tracker += 1
            continue

        if did_we_catch_the_file_tracker == 0: # we failed to account for this raw file in the above if/else cases
            err_msg_unknown = f'{raw} found under {subject} failed to be copied to {subject_paradigm_visit_folder}... \nThe file in question may have a more severe typo.'
            logging.error(err_msg_unknown) # compose an error message
            print(err_msg_unknown)
        else:
            continue



logging.basicConfig(filename=mgr_cfg.log_filename, level=logging.DEBUG)
for subject in mgr_cfg.potential_subjects_tal: # loop through subjects in Tal's MEGRAID folder
    # filter potential subjects - check if the folder name is that of a valid subject
    if mgr_fcn.is_not_valid_subject(subject):
        continue # now we have a valid subject (subject ID: 012345 or AC#0123)

    subject_megraid_dir = os.path.join(mgr_cfg.megraid_dir_tal, subject) # locate subject's MEGRAID folder
    # create dictionary of visit dates and paradigm file matches
    relevant_subject_files_dict = mgr_fcn.refine_search_by(subject_megraid_dir, mgr_cfg.years_of_interest, mgr_cfg.paradigms)

    subject = subject.split('_')[1]

    for visit_paradigm_pair, list_of_raws in relevant_subject_files_dict.items():

        subject_megraid_visit_folder, subject_paradigm_visit_folder, fixation = mgr_fcn.prepare_to_copy_files(
            subject, mgr_cfg.meg_dir, subject_megraid_dir, visit_paradigm_pair, list_of_raws)

        copy_files_if_needed_and_check(list_of_raws, subject, subject_megraid_visit_folder, subject_paradigm_visit_folder, fixation)

#mgr_fcn.compose_and_send_email_update(mgr_cfg.log_filename, mgr_cfg.current_datetime, mgr_cfg.email_recipient)
