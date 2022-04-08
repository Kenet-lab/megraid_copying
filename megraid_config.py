import os
from time import strftime

### TOP LEVEL - hard-coded variables/values, locations
meg_dir = '/autofs/cluster/transcend/MEG'
erm_dir = os.path.join(meg_dir, 'erm')

megraid_dir_tal = '/autofs/space/megraid_research/MEG/tal'
megraid_dir_kenet = '/autofs/space/megraid_research/MEG/kenet'
potential_subjects_tal = os.listdir(megraid_dir_tal)
potential_subjects_kenet = os.listdir(megraid_dir_kenet)
#potential_subjects = potential_subjects_tal + potential_subjects_kenet # list the contents of Tal's MEGRAID folder (i.e. subject IDs)

current_datetime = strftime('%Y%m%d-%H%M%S')
#log_filename = os.path.join(meg_dir, 'megraid_copying', 'logs', f'MEGRAID_copying_script_{current_datetime}.log')
log_filename = f'MEGRAID_copying_script_{current_datetime}.log'

### LOW LEVEL - user-defined parameters and variables, highly subject to change!
email_recipient = ['tal.kenet@mgh.harvard.edu']

# date specification(s) for narrowing a search for visits to copy
# years_of_interest = ['2021', '2022']
years_of_interest = ['2022']

# paradigm specification(s) for narrowing a search for data to copy
# paradigms = ['AttenVis', 'AttenAud', 'erm', 'fix', 'ASSRnew', 'ASSR', 'tac_vib_only', 'speech']
paradigms = ['erm','AttenAud']
