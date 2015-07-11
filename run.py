#!/usr/bin/env python

import argparse
from trello import TrelloClient
from trello.util import create_oauth_token
from pyhabit import HabitAPI
from habitrello import HabiTrello
from habitrello.keys import get_keys, save_keys

def get_args():
	parser = argparse.ArgumentParser(description='Sync HabitRPG and Trello tasks!')
	parser.add_argument('--skip-todos', dest='skip_todos', action='store_true', 
		help='Skip processing Todos')
	parser.add_argument('--skip-dailies', dest='skip_dailies', action='store_true',
		help='Skip processing Dailies')
	parser.add_argument('--skip-habits', dest='skip_habits', action='store_true',
		help='Skip processing Habits')
	parser.add_argument('--key-file', dest='key_file', default='keys.json',
		help='File to store the API keys and tokens')
	return parser.parse_args()


def setup_trello(keys):
	trello_api_secret = keys.get('trello_api_secret', '')
	trello_api_key = keys.get('trello_api_key', '')
	if not trello_api_secret or not trello_api_key:
		print 'Trello API Key and API Secret are REQUIRED. Please fill them into the provided key file.'
	trello_token = keys.get('trello_token', '')
	trello_token_secret = keys.get('trello_token_secret', '')
	# if we don't have trello tokens, we need to call OAuth.
	if not trello_token or not trello_token_secret:
		access_token = create_oauth_token(None, None, trello_api_key, trello_api_secret, 'HabiTrello')
		keys['trello_token'] = access_token.get('oauth_token', None)
		keys['trello_token_secret'] = access_token.get('oauth_token_secret', None)

	# Create our Trello API client
	return TrelloClient(
				api_key=keys['trello_api_key'],
				api_secret=keys['trello_api_secret'],
				token=keys['trello_token'],
				token_secret=keys['trello_token_secret']
			), keys


def setup_habit(keys):
	habit_uuid = keys.get('habit_uuid', '')
	habit_api_key = keys.get('habit_api_key', '')

	if not habit_uuid or not habit_api_key:
		print 'Habit RPG UUID and API Key are REQUIRED. Please fill them into the provided key file.'

	return HabitAPI(habit_uuid, habit_api_key)


def main():

	args = get_args()

	keys = get_keys(args.key_file)

	api = client = None

	try:
		# Get the tasks for the user in HabitRPG
		api = setup_habit(keys)

		client, keys = setup_trello(keys)

	except:
		print 'Error while setting up HabitRPG API and Trello API'
	finally:
		save_keys(keys)

	HabiTrello(api, client, args).main()


if __name__ == "__main__":
	main()
