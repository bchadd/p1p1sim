import requests
from datetime import datetime
from os import path
import pytz
import simplejson as json
import ijson

def write_bulk_json() -> None:
    bulk_res = requests.get('https://api.scryfall.com/bulk-data/oracle-cards')
    bulk_res.raise_for_status()
    res_json = bulk_res.json()
    with open('bulk-data.json','w') as file:
        json.dump(res_json, file)

def update_bulk_json() -> None:
    ## Overwrite local bulk json if response's 'updated_at'
    ## timestamp is more recent than local json's mod timestamp.
    ## Raises HTTPError if Scryfall API is not responding.
    bulk_res = requests.get('https://api.scryfall.com/bulk-data/oracle-cards')
    bulk_res.raise_for_status()
    res_json = bulk_res.json()
    res_dt = datetime.fromisoformat(res_json['updated_at'])
    last_updated_dt = datetime.fromtimestamp(path.getmtime('bulk-data.json'),pytz.UTC)
    if res_dt > last_updated_dt:
        new_json_uri = res_json['uri']
        new_json_res = requests.get(new_json_uri)
        new_json_res.raise_for_status()
        new_json = new_json_res.json()
        with open('bulk-data.json','w') as file:
            json.dump(new_json, file)

def filter_json_for_(oracle_json: json, cube_list: list) -> json:
    ## recreate oracle card json for cube cards only
    filtered_cards = []
    with open('bulk-data.json','r') as f:
        cards = ijson.items(f,'item')
        for card in cards:
            if card.get('name') in cube_list:
                filtered_cards.append(card)
    return json.dumps(filtered_cards)
    
def extract_info_from_(filtered_json: json) -> json:
    ## extract name and .png file from each card
    extracted_json = []
    for card in ijson.items(filtered_json,'item'):
        extracted_card_info = {}
        extracted_card_info['name'] = card['name']
        extracted_card_info['png'] = card['image_uris']['png']
        extracted_json.append(extracted_card_info)
    return json.dumps(extracted_json)