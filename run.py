#!/usr/bin/env python

import argparse
from trello import TrelloClient
from trello.util import create_oauth_token
from pyhabit import HabitAPI
from habitrello import HabiTrello
from habitrello.keys import habit_uuid, habit_api_key, trello_api_key,\
	trello_api_secret, trello_token, trello_token_secret

def get_args():
	parser = argparse.ArgumentParser(description='Sync HabitRPG and Trello tasks!')
	parser.add_argument('--skip-todos', dest='skip_todos', action='store_true',
						help='Skip processing Todos')
	parser.add_argument('--skip-dailies', dest='skip_dailies', action='store_true',
						help='Skip processing Dailies')
	parser.add_argument('--skip-habits', dest='skip_habits', action='store_true',
						help='Skip processing Habits')
	return parser.parse_args()


def setup_trello():
	final_trello_token = trello_token
	final_trello_token_secret = trello_token_secret

	# if we don't have trello tokens, we need to call OAuth.
	if not trello_token or not trello_token_secret:
		access_token = create_oauth_token(None, None, trello_api_key, trello_api_secret, 'HabiTrello')
		final_trello_token = access_token.get('oauth_token', None)
		final_trello_token_secret = access_token.get('oauth_token_secret', None)

	# Create our Trello API client
	return TrelloClient(
				api_key=trello_api_key,
				api_secret=trello_api_secret,
				token=final_trello_token,
				token_secret=final_trello_token_secret
			)


def main():

	args = get_args()

	# Get the tasks for the user in HabitRPG
	api = HabitAPI(habit_uuid, habit_api_key)

	client = setup_trello()

	HabiTrello(api, client).main(args.skip_todos, args.skip_dailies, args.skip_habits)

if __name__ == "__main__":
	main()
