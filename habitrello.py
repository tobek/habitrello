from habitrpg import HabitAPI
from trello import *
from trello.util import *
from keys import habit_uuid, habit_api_key, trello_api_key, trello_api_secret, trello_token, trello_token_secret

def processDailies(trello_dailies_list, dailies, board, new_board, api):
	# Dailies
	trello_dailies_dict = {}
	# If we didn't find the list, we have to make a new one
	# and again assume all the Dailies were finished
	if not trello_dailies_list:
		trello_dailies_list = board.add_list('Dailies')
	# Otherwise, we check which cards haven't been finished
	else:
		trello_dailies = trello_dailies_list.list_cards()
		# If the list was closed, we open it
		# and mark all of the dailies as completed
		if trello_dailies_list.closed:
			trello_dailies_list.open()
			if not new_board:
				for dailiy_id,daily in dailies.items():
					completeDaily(daily, api)

		# Now, we iterate through all of the remaining cards and remove them
		for trello_daily in trello_dailies:
			trello_dailies_dict[trello_daily.description] = trello_daily
			if trello_daily.description in dailies:
				print "Daily " + trello_daily.name + " was not done today!"
			else:
				new_daily = api.create_task(HabitAPI.TYPE_DAILY, trello_daily.name)
				print "Daily " + trello_daily.name + " was created!"
				dailies[new_daily["id"]] = new_daily
			trello_daily.delete()

	# then we add in the new cards
	for daily_id,daily in dailies.items():
		if daily_id not in trello_dailies_dict:
			completeDaily(daily, api)
		trello_dailies_list.add_card(daily["text"], daily_id)

def completeDaily(daily, api):
	daily["completed"] = True
	print "Daily " + daily["text"] + " was finished!"
	print api.update_task(daily["id"], daily)

def processHabits(trello_habits_list, habits, board, new_board, api):
	# Habits
	trello_habits_dict = {}
	if not trello_habits_list:
		trello_habits_list = board.add_list('Habits')
	else:
		trello_habits = trello_habits_list.list_cards()

		if trello_habits_list.closed:
			trello_habits_list.open()
			if not new_board:
				for habit_id,habit in habits.items():
					upArrowHabit(habit)

		for trello_habit in trello_habits:
			trello_habits_dict[trello_habit.description] = trello_habit
			if trello_habit.description in habits:
				downArrowHabit(habits[trello_habit.description], api)
			else:
				new_habit = api.create_task(HabitAPI.TYPE_HABIT, trello_habit.name)
				print "Habit " + trello_habit.name + " was created!"
				habits[new_habit["id"]] = new_habit
			trello_habit.delete()

	for habit_id,habit in habits.items():
		if habit_id not in trello_habits_dict:
			upArrowHabit(habit, api)
		trello_habits_list.add_card(habit["text"], habit_id)

def upArrowHabit(habit, api):
		api.perform_task(habit["id"], HabitAPI.DIRECTION_UP)
		print "Habit " + habit["text"] + " was finished!"

def downArrowHabit(habit, api):
		print "Habit " + habit["text"] + " was not finished!"
		api.perform_task(habit["id"], HabitAPI.DIRECTION_DOWN)


def processTodos(trello_todos_list, todos, board, new_board, api, todos_completed):
	# Todos
	trello_todos_dict = {}
	if not trello_todos_list:
		trello_todos_list = board.add_list('Todos')
	else:
		trello_todos = trello_todos_list.list_cards()
		if trello_todos_list.closed:
			trello_todos_list.open()
			if not new_board:
				for todo_id,todo in todos.items():
					completeTodo(todo, api)

		for trello_todo in trello_todos:
			trello_todos_dict[trello_todo.description] = trello_todo
			# If we have a task in Trello not in HabitRPG, it means they added it in Trello
			if trello_todo.description not in todos and trello_todo.description not in todos_completed:
				new_task = api.create_task(HabitAPI.TYPE_TODO, trello_todo.name)
				print "Todo " + trello_todo.name + " was created!"
				todos[new_task["id"]] = new_task
				trello_todos_dict[new_task["id"]] = new_task

			else:
				print "Todo " + trello_todo.name + " was not done today!"
			trello_todo.delete()

	for todo_id,todo in todos.items():
		if todo_id not in trello_todos_dict:
			completeTodo(todo, api)
		trello_todos_list.add_card(todo["text"], todo_id)

def completeTodo(todo, api):
	todo["completed"] = True
	print "Todo " + todo["text"] + " was finished!"
	print todo
	print api.update_task(todo["id"], todo)

def main(habit_uuid, habit_api_key, trello_api_key, trello_api_secret, trello_token, trello_token_secret):
	# Get the tasks for the user in HabitRPG
	api = HabitAPI(habit_uuid, habit_api_key)
	tasks = api.tasks()
	# Populate the separate lists
	# of habits, dailies, and todos
	habits = {}
	dailies = {}
	todos = {}
	todos_completed = {}
	for task in tasks:
		if task["type"] == HabitAPI.TYPE_HABIT:
			habits[task["id"]] = task
		elif task["type"] == HabitAPI.TYPE_DAILY:
			dailies[task["id"]] = task
		elif task["type"] == HabitAPI.TYPE_TODO:
			if task["completed"] == True:
				todos_completed[task["id"]] = task
			else:
				todos[task["id"]] = task

	# if we don't have trello tokens, we need to call OAuth.
	if not trello_token or not trello_token_secret:
		access_token = create_oauth_token(None, None, trello_api_key, trello_api_secret, 'HabiTrello')
		trello_token = access_token['oauth_token']
		trello_token_secret = access_token['oauth_token_secret']

	# Create our Trello API client
	client = TrelloClient(
	                      api_key = trello_api_key,
	                      api_secret = trello_api_secret,
	                      token = trello_token,
	                      token_secret = trello_token_secret
		)

	habitrello_board = None

	# Loop through the user's boards until we find the Habit RPG one
	for board in client.list_boards():
		if board.name == 'Habit RPG':
			habitrello_board = board
			break

	new_board = False
	# if we don't have a Habit RPG borad, then we have to make a new one
	if not habitrello_board:
		habitrello_board = client.add_board('Habit RPG')
		new_board = True
	# if the board we found was closed, then we open it
	# and assume that the user had finished all of the dailies, habits, and tasks
	elif habitrello_board.closed:
		habitrello_board.open()
		up_dailies = True
		up_todos = True
		up_dailies = True

	trello_habits_list = None
	trello_todos_list = None
	trello_dailies_list = None

	# Now we look in the Habit RPG board for all of the lists
	for board_list in habitrello_board.get_lists('all'):
		# if we find the Dailies list
		if board_list.name == 'Dailies':
			# We grab the object
			trello_dailies_list = board_list
		# Rinse and repeat for Todos and Habits
		elif board_list.name == 'Todos':
			trello_todos_list = board_list
		elif board_list.name == 'Habits':
			trello_habits_list = board_list
		# Finally, we close any lists that aren't related to Habit RPG
		else:
			board_list.close()

	#processDailies(trello_dailies_list, dailies, board, new_board, api)
	#processHabits(trello_habits_list, habits, board, new_board, api)
	processTodos(trello_todos_list, todos, board, new_board, api, todos_completed)

main(habit_uuid, habit_api_key, trello_api_key, trello_api_secret, trello_token, trello_token_secret)