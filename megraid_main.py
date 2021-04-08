import os
import shutil
import logging
import megraid_config as mgr_cfg
import megraid_functions as mgr_fcn

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
            logging.error(f'There exists a typo between {subject} and one of its filenames: {raw}\n')
            did_we_catch_the_file_tracker += 1
            continue
        elif mgr_fcn.redcap_is_not_consistent(subject, mgr_cfg.redcap_records, subject_paradigm_visit_folder):
            # RedCap consistency logging occurs in megraid_functions.redcap_is_not_consistent function due to verbosity
            did_we_catch_the_file_tracker +=1
            continue
        elif not os.path.isfile(dest_file): # copy the file and log the file being copied
            logging.info(f'Copying {source_file} to {dest_file} for {subject}\n')
            shutil.copyfile(source_file, dest_file)
            did_we_catch_the_file_tracker += 1
        elif os.path.isfile(dest_file):
            logging.info(f'Tried copying {source_file} to {dest_file} for {subject}, but it already exists!\n')
            did_we_catch_the_file_tracker += 1
            continue

        if did_we_catch_the_file_tracker == 0: # we failed to account for this raw file in the above if/else cases
            err_msg = f'{raw} found under {subject} failed to be copied to {subject_paradigm_visit_folder}...\n' \
                      f'The file in question may have a more severe typo... It was consistent with RedCap, too.'
            logging.error(err_msg) # compose an error message
        else:
            continue



logging.basicConfig(filename=mgr_cfg.log_filename, level=logging.DEBUG)
for subject in mgr_cfg.potential_subjects: # loop through subjects in Tal's MEGRAID folder
    # filter potential subjects - check if the folder name is that of a valid subject
    if mgr_fcn.is_not_valid_subject(subject):
        continue # now we have a valid subject (subject ID: 012345 or AC#0123)

    subject_megraid_dir = os.path.join(mgr_cfg.megraid_dir, subject) # locate subject's MEGRAID folder
    # create dictionary of visit dates and paradigm file matches
    relevant_subject_files_dict = mgr_fcn.refine_search_by(subject_megraid_dir, mgr_cfg.years_of_interest, mgr_cfg.paradigms)

    for visit_paradigm_pair, list_of_raws in relevant_subject_files_dict.items():

        subject_megraid_visit_folder, subject_paradigm_visit_folder, fixation = mgr_fcn.prepare_to_copy_files(
            subject, mgr_cfg.meg_dir, subject_megraid_dir, visit_paradigm_pair, list_of_raws)

        copy_files_if_needed_and_check(list_of_raws, subject, subject_megraid_visit_folder, subject_paradigm_visit_folder, fixation)

mgr_fcn.compose_and_send_email_update(mgr_cfg.log_filename, mgr_cfg.current_datetime, mgr_cfg.email_recipient)
