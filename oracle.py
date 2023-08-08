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
        with open('bulk-data.json','wb') as file:
            file.write(bulk_res.content)

def get_oracle_uri() -> str:
    with open('bulk-data.json','r') as bulk_json:
        loaded_bulk_json = json.load(bulk_json)
        return loaded_bulk_json['download_uri']

def update_oracle_json(oracle_uri: str) -> None:
    with requests.get(oracle_uri,stream=True) as new_oracle_res:
        with open('oracle-cards.json','wb') as oracle_json:
            for chunk in new_oracle_res.iter_content(chunk_size=64):
                oracle_json.write(chunk)

def filter_oracle_json_for_(cube_list: list) -> json:
    ## recreate oracle card json for cube cards only
    filtered_cards = []
    with open('oracle-cards.json','r',encoding='UTF-8') as file:
        cards = ijson.items(file,'item')
        for card in cards:
            if card.get('name') in cube_list:
                filtered_cards.append(card)
    return json.dumps(filtered_cards)
    
def extract_info_from_(filtered_json: json) -> json:
    ## extract id, name, and .png uri from each card
    extracted_json = []
    cards = ijson.items(filtered_json,'item')
    for card in cards:
        extracted_card_info = {}
        extracted_card_info['id'] = card['id']
        extracted_card_info['name'] = card['name']
        extracted_card_info['png'] = card['image_uris']['png']
        extracted_json.append(extracted_card_info)
    return json.dumps(extracted_json)