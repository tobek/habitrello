import json
from habitrello.utils import print_message

DEFAULT_KEYS = {
        'habit_uuid': '',
        'habit_api_key': '',
        'trello_api_key': '',
        'trello_api_secret': '',
        'trello_token': '',
        'trello_token_secret': ''
        }

def get_keys(file='keys.json'):
    try:
        keys_json = open(file, 'rw').read()
    except IOError:
        print_message('Could not find file %s for keys.' % file)
        save_keys(DEFAULT_KEYS, file)
        return DEFAULT_KEYS

    try:
        keys = json.loads(keys_json)
    except IOError:
        print_message('Could not parse the JSON for the Keys file. Please make sure it is proper JSON!')

    return keys

def save_keys(new_keys, file='keys.json'):
    try:
        open(file, 'w').write(json.dumps(new_keys, sort_keys=True, indent=4, separators=(',', ': ')))
    except IOError:
        print_message('Failed to write Keys to %s file!' % file)

    return new_keys
