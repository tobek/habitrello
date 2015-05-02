from habitrpg import HabitAPI
from trello import TrelloClient
from keys import habit_uuid, habit_api_key, trello_api_key, trello_api_secret, trello_token, trello_token_secret


api = HabitAPI(uuid, api_key)
tasks = api.tasks()

client = TrelloClient(
                      api_key = 
	)