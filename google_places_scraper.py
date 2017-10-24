# To scrape public data using Google's places API

# Loading packages
import os
import json
import time
import urllib
import requests
import numpy as np

import warnings
warnings.filterwarnings('ignore')

# Define config file path that contains the access key
this_dir, this_filename = os.path.split(__file__)
CONFIG_PATH = os.path.join(this_dir, "config.json")

# Import access Keys
with open(CONFIG_PATH, 'r') as json_data_file:
    access_keys = json.load(json_data_file)
api_key = access_keys['google_places']['api_key']

# Define Google places api URL
place_seach_query = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='
place_id_query = 'https://maps.googleapis.com/maps/api/place/details/json?placeid='


# Function to decode any string type to unicode
def to_unicode(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = obj.decode(encoding, errors='ignore')
    return obj


# Function to encode any string to bytes
def to_bytes(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, str):
            obj = obj.encode(encoding)
    return obj


# Function to get place content
def get_place_content(place_url):
    content = None
    max_attempt = 5

    while max_attempt:
        try:
            content = requests.get(place_url, verify=False)
            return content
        except requests.exceptions.Timeout:
            time.sleep(np.random.randint(2, 3))
            max_attempt -= 1
        except requests.exceptions.RequestException:
            return content

    return content


# Function to get place results
def get_place_results(content):
    # Get the place ids of the places found for the given search keyword
    place_id_list = [entry['place_id'] for entry in content.json()['results']]
    result_list = []
    for place_id in place_id_list:
        place_detail_url = place_id_query + place_id + '&key=' + api_key
        try:
            resp = requests.get(place_detail_url, verify=False).json()
            result = resp[u'result'] if resp[u'status'] == u"OK" else {}
        except requests.exceptions.RequestException:
            result = {}
        result_list.append(result)
    return result_list


# Function to retrieve data for a search_query
def get_places_search_data(search_keyword):
    search_keyword = to_bytes(search_keyword)
    cleaned_address = urllib.quote_plus(search_keyword.strip())
    place_url = place_seach_query + cleaned_address + '&key=' + api_key

    # To get the place content
    content = get_place_content(place_url)

    # Check if there is an error
    try:
        error_msg = content.json()['error_message']
        raise(error_msg)
        return []
    except AttributeError:
        return []
    except KeyError:
        pass

    # Get the details of each place id
    results = get_place_results(content)
    return results


def main():
    # Get data for a given place
    place_name = 'some_place'
    results = get_places_search_data(place_name)

    for each_result in results:
        print to_bytes(each_result['name'])
        print to_bytes(each_result['formatted_address'])
        print to_bytes(each_result['website'])
