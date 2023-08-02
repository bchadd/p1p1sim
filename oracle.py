import requests
from datetime import datetime
from os import path
import pytz
import simplejson as json
import ijson

def write_bulk_json() -> None:
    bulk_res = requests.get('https://api.scryfall.com/bulk-data/oracle-cards')
    bulk_res.raise_for_status()
    with open('bulk-data.json','wb') as file:
        file.write(bulk_res.content)

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
        new_json_uri = res_json['download_uri']
        new_json_res = requests.get(new_json_uri)
        new_json_res.raise_for_status()
        with open('bulk-data.json','wb') as file:
            file.write(new_json_res.content)

def extract_oracle_json() -> None:
    with open('bulk-data.json','r') as bulk_json:
        loaded_bulk_json = json.load(bulk_json, encoding='UTF-8')
        uri = loaded_bulk_json['download_uri']
        oracle_res = requests.get(uri)
        oracle_res.raise_for_status()
        with open('oracle-cards.json','wb') as oracle_json:
            oracle_json.write(oracle_res.content)

def filter_oracle_json_for_(cube_list: list) -> json:
    ## recreate oracle card json for cube cards only
    filtered_cards = []
    with open('oracle-cards.json','r', encoding='UTF-8') as file:
        cards = ijson.items(file,'item')
        for card in cards:
            if card.get('name') in cube_list:
                filtered_cards.append(card)
    return json.dumps(filtered_cards)
    
def extract_info_from_(filtered_json: json) -> json:
    ## extract name, mtgo id, and .png file from each card
    extracted_json = []
    cards = ijson.items(filtered_json,'item')
    for card in cards:
        extracted_card_info = {}
        extracted_card_info['id'] = card['id']
        extracted_card_info['name'] = card['name']
        extracted_card_info['png'] = card['image_uris']['png']
        extracted_json.append(extracted_card_info)
    return json.dumps(extracted_json)