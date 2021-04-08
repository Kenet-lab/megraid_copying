import os
from time import strftime
from requests import post

### TOP LEVEL - hard-coded variables/values, locations
meg_dir = '/autofs/cluster/transcend/MEG'
erm_dir = os.path.join(meg_dir, 'erm')

megraid_dir_tal = '/autofs/space/megraid_research/MEG/tal'
megraid_dir_kenet = '/autofs/space/megraid_research/MEG/kenet'
potential_subjects_tal = os.listdir(megraid_dir_tal)
potential_subjects_kenet = os.listdir(megraid_dir_kenet)
potential_subjects = potential_subjects_tal + potential_subjects_kenet # list the contents of Tal's MEGRAID folder (i.e. subject IDs)

current_datetime = strftime('%Y%m%d-%H%M%S')
log_filename = f'MEGRAID_copying_script_{current_datetime}.log'

redcap_url = 'https://redcap.partners.org/redcap/api/'

### LOW LEVEL - user-defined parameters and variables, highly subject to change!
email_recipient = ['sgraham11@mgh.harvard.edu', 'tal.kenet@mgh.harvard.edu']

# date specification(s) for narrowing a search for visits to copy
years_of_interest = ['2020']

# paradigm specification(s) for narrowing a search for data to copy
paradigms = ['AttenVis', 'AttenAud', 'erm', 'fix', 'ASSRnew', 'ASSR', 'tac_vib_only']

# REDCAP
TOKEN = 'E0452CFAD28AECECCDA91175D4289424' # REDCap "TRANSCEND All Projects" project token
payload = {'token': TOKEN, 'format': 'json', 'content': 'record', 'type': 'flat'}
response = post(redcap_url, data=payload)
if response.status_code == 200: # the API accepted our request
    redcap_records = response.json() # list of dictionaries
