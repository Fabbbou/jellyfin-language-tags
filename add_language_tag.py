##
# This has been tested the 20th December 2024
# When the process is done, you should launch a Library scan in Jellyfin to apply tags everywhere.
# 
# Vars to set:
# JELLYFIN_URL (ex: http://your/jellyfin:PORT)
# USERNAME (tested on Admin account only)
# PASSWORD
# and run ! 
#
# Dependencies:
# I used python3, and requests lib...
# pip install requests (if you dont have it, but I guess it's a common lib to have)
# 
# The process took me 10 minutes for ~500 files.
#
# It will add a tag based on the Audio tracks in the videos.
# The format of the tag is : language_<language_found> for example: language_eng for english
# If the tag already exists, it will not duplicate, so you can run this script safely every month for example.
# 
# If you wanna see more details of the script during the process, feel free to enable VERBOSE by changing the var.
# DEBUG is really to debug, as it print some http response.
# The NUMBER_PER_BATCH is based at 10, to process items because it was ok for me, but feel free to change it as well if you want
# 
#
# Special thanks to this gist that gave me the piece of example to start the project https://gist.github.com/mcarlton00/f7bd7218828ed465ce0f309cebf9a247
#
#
#
# Some part of the Jellyfin API doesn't give enough info without an admin login auth. Maybe there is some way to fix it but it took me already enough time to setup :p
# BTW, don't EVER do UpdateItems (POST to /Items/{item_id}) without re-using the exact result of  GET /Items/{item_id} endpoint as input to the update, or it will corrupt your metadata (Jellyfin doesn't like it for some reason...) 
#
# Know bugs:
# - Some video may not have a Language define in the Audio, resulting in a language_ tag added.
#       I kept it like that cause it may help you edit manually if you care... I dont !
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

def search_items_movie(startindex, limit):
    url = f"{JELLYFIN_URL}/Items?Recursive=True&IncludeItemTypes=Episode,Movie&filters=IsNotFolder&fields=&StartIndex={startindex}&Limit={limit}"
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

def get_more_infos(item_id):
    url = f"{JELLYFIN_URL}/Items/{item_id}"
    response = requests.get(url, headers=HEADERS, json=auth_data)  # Use headers for authentication
    if DEBUG:
        print(f"Response ({response.status_code}): {response.text}")  # Debugging
    if response.status_code == 200:
        results = response.json()
        return results
    return None

def get_audio_languages(item_id):
    """Get audio languages for a specific item."""
    url = f"{JELLYFIN_URL}/Items/{item_id}/PlaybackInfo"
    response = requests.get(url, headers=HEADERS, json=auth_data)  # Use headers for authentication
    if DEBUG:
        print(f"Response ({response.status_code}): {response.text}")  # Debugging
    if response.status_code == 200:
        media_sources = response.json().get("MediaSources", [])
        languages = []
        for sources in media_sources:
            media_stream = sources.get("MediaStreams", [])
            # print(media_stream)
            for stream in media_stream:
                if stream.get("Type") == "Audio":
                    # print(stream.get("Language",""))
                    languages.append(stream.get("Language",""))
        return languages
    print(f"Failed to fetch audio streams for item ID {item_id}.")
    return []

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
def append_language_to_tags(metadata,language_array):
    for lang in language_array:
        tag = f"language_{lang}"
        if tag not in metadata['Tags']:
            metadata['Tags'].append(tag)
def tag_movie(movie_item_id):
    metadata = get_more_infos(item["id"])
    language_array = get_audio_languages(metadata["Id"])
    if VERBOSE:
        print(f"Fetched languages:{language_array}")
    append_language_to_tags(metadata,language_array)
    update_item(metadata)

def update_tags(items):
    all_languages_tags = []
    for item in items:
        metadata = get_more_infos(item["id"])
        language_array = get_audio_languages(metadata["Id"])
        if VERBOSE:
            print(f"Fetched languages:{language_array}")
        append_language_to_tags(metadata,language_array)
        update_item(metadata)
        for lang_tag in language_array:
            if lang_tag not in all_languages_tags:
                all_languages_tags.append(lang_tag)
    return all_languages_tags

def search_series(startindex, limit):
    url = f"{JELLYFIN_URL}/Items?Recursive=True&IncludeItemTypes=Series&StartIndex={startindex}&Limit={limit}"
    response = requests.get(url, headers=HEADERS, json=auth_data)
    # if DEBUG:
    # print(f"Response ({response.status_code}): {response.text}")  # Debugging
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

def search_seasons(serie_id):
    url = f"{JELLYFIN_URL}/Items?Recursive=True&IncludeItemTypes=Season&ParentId={serie_id}"
    response = requests.get(url, headers=HEADERS, json=auth_data)
    # if DEBUG:
    # print(f"Response ({response.status_code}): {response.text}")  # Debugging
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

def search_episodes(season_id):
    url = f"{JELLYFIN_URL}/Items?Recursive=True&IncludeItemTypes=Episode&ParentId={season_id}"
    response = requests.get(url, headers=HEADERS, json=auth_data)
    # if DEBUG:
    # print(f"Response ({response.status_code}): {response.text}")  # Debugging
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


##### Main process #####

## Process Movies

movie_count = get_count("Movie")
print(f"Movie count: {movie_count}")
number_to_proceed = STOP_AT if STOP_AT != 0 else movie_count
is_process_ended = False
next_start = 0
while not is_process_ended:
    print(f"Processing {next_start} to {next_start+NUMBER_PER_BATCH}")
    items = search_items_movie(next_start,NUMBER_PER_BATCH)
    if VERBOSE:
        print(items)
    if len(items) < NUMBER_PER_BATCH or number_to_proceed <= 0:
        is_process_ended = True
        print("Last batch!")
    update_tags(items)
    number_to_proceed = number_to_proceed - NUMBER_PER_BATCH
    next_start = next_start + NUMBER_PER_BATCH
print ("Process completed.")


## Process Series

serie_count = get_count("Series")
print(f"Series count: {serie_count}")
languages = []
series_items = search_series(0, serie_count)
for serie_item in series_items:
    print(f"For serie {serie_item['name']} {serie_item['id']}")
    seasons_items = search_seasons(serie_item["id"])
    for season_item in seasons_items:
        print(season_item)
        episodes_items = search_episodes(season_item["id"])
        languages_episodes_tags = update_tags(episodes_items)
        for lang_tag in languages_episodes_tags:
            if lang_tag not in languages:
                languages.append(lang_tag)
                print(f"Found lang {lang_tag}")
        metadata_season = get_more_infos(season_item["id"])
        append_language_to_tags(metadata_season,languages)
        update_item(metadata_season)
    metadata_serie = get_more_infos(serie_item["id"])
    append_language_to_tags(metadata_serie,languages)
    update_item(metadata_serie)
    languages = []


##### Tools to help debug #####

# Debug a specific ID if something went wrong
# metadata = get_more_infos("03b1adfdb870388372dcfa3c40720090")
# language_array = get_audio_languages(metadata["Id"])
# print(language_array)
