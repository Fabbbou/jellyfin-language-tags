##
# This is a cleaning script, in case you customized add_language_tag.py script but made mistakes
# It will remove the language_xxx tags for every series and every movies 
##
import os

import requests
JELLYFIN_URL = os.getenv("JELLYFIN_URL", 'http://localhost:8096') # To be changed !
#It has to be the admin user to be sure it works
USERNAME = os.getenv("JELLYFIN_USERNAME", 'username')
PASSWORD = os.getenv("JELLYFIN_PASSWORD", 'password')


#set 0 to do all the files in the Jellyfin server
STOP_AT = 0
# increase or decrease if needed to help debug
NUMBER_PER_BATCH = 10
VERBOSE = False
DEBUG = False


##### AUTH #####
authorization = 'MediaBrowser Client="python-script", Device="add_language_tags", DeviceId="33fc255a-be9b-11ef-993c-272469e0c800", Version="1.0.0"'
HEADERS = {
     'Authorization': authorization,
}
auth_data = {
    'username': USERNAME,
    'Pw': PASSWORD
}
# Authenticate to server
r = requests.post(JELLYFIN_URL + '/Users/AuthenticateByName', headers=HEADERS, json=auth_data)
# Retrieve auth token and user id from returned data
token = r.json().get('AccessToken')
user_id = r.json().get('User').get('Id')
# Update the headers to include the auth token
HEADERS['Authorization'] = f'{authorization}, Token="{token}"'


##### Functions #####
def get_count(item_type):
    url = f"{JELLYFIN_URL}/Items?Recursive=True&IncludeItemTypes={item_type}&StartIndex=0&Limit=0"
    response = requests.get(url, headers=HEADERS, json=auth_data)  # Use headers for authentication
    if DEBUG:
        print(f"Response ({response.status_code}): {response.text}")  # Debugging
    if response.status_code == 200:
        results = response.json().get("Items", [])
        return response.json().get("TotalRecordCount",1)

def search_items(filter, startindex, limit):
    url = f"{JELLYFIN_URL}/Items?Recursive=True&IncludeItemTypes={filter}&&StartIndex={startindex}&Limit={limit}"
    response = requests.get(url, headers=HEADERS, json=auth_data)  # Use headers for authentication
    if DEBUG:
        print(f"Response ({response.status_code}): {response.text}")  # Debugging
    if response.status_code == 200:
        results = response.json().get("Items", [])
        items = []
        for item in results:
            items.append({
                "id": item.get("Id"),
                "name": item.get('Name','no name found'),
            })
        return items
    return None

def delete_language_to_tags(metadata):
    for tag in metadata['Tags']:
        tag_to_delete = "language_"
        if tag.startswith(tag_to_delete):
            metadata['Tags'].remove(tag)

def update_tags(items):
    all_languages_tags = []
    for item in items:
        metadata = get_more_infos(item["id"])
        delete_language_to_tags(metadata)
        update_item(metadata)
    return all_languages_tags

def update_item(metadata):
    """Add a tag to a specific item."""
    url = f"{JELLYFIN_URL}/Items/{metadata['Id']}"
    payload = metadata
    response = requests.post(url, json=payload, headers=HEADERS)  # Use headers for authentication
    if DEBUG:
        print(f"Response ({response.status_code}): {response.text}")  # Debugging
    if response.status_code == 204:
        if VERBOSE:
            print(f"Tag added to id {metadata['Id']} name: {metadata['Name']}.")
    else:
        print(f"Failed to add tag: {response.text}")

def get_more_infos(item_id):
    url = f"{JELLYFIN_URL}/Items/{item_id}"
    response = requests.get(url, headers=HEADERS, json=auth_data)  # Use headers for authentication
    if DEBUG:
        print(f"Response ({response.status_code}): {response.text}")  # Debugging
    if response.status_code == 200:
        results = response.json()
        return results
    return None

def clear(filters_to_clean):
    count = get_count(filters_to_clean)
    print(f"count: {count}")
    number_to_proceed = STOP_AT if STOP_AT != 0 else count
    is_process_ended = False
    next_start = 0
    while not is_process_ended:
        print(f"Processing {next_start} to {next_start+NUMBER_PER_BATCH}")
        items = search_items(filters_to_clean, next_start,NUMBER_PER_BATCH)
        if VERBOSE:
            print(items)
        if len(items) < NUMBER_PER_BATCH or number_to_proceed <= 0:
            is_process_ended = True
            print("Last batch!")
        update_tags(items)
        number_to_proceed = number_to_proceed - NUMBER_PER_BATCH
        next_start = next_start + NUMBER_PER_BATCH
        print ("Process completed.")

clear("Series")
clear("Movie")