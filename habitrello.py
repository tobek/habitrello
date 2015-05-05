import argparse
from datetime import date, time, timedelta
from pyhabit import HabitAPI
from trello import *
from trello.util import *
from keys import habit_uuid, habit_api_key, trello_api_key, trello_api_secret, trello_token, trello_token_secret

class HabiTrello(object):

	def __init__(self, api, client):
		self.api = api
		self.client = client
		self.tasks = api.tasks()
		self.labels = {}
		self.habits = {}
		self.habits_dict = {}
		self.habits_list = None
		self.dailies = {}
		self.dailies_dict = {}
		self.dailies_list = None
		self.todos = {}
		self.todos_dict = {}
		self.todos_list = None

	def process_dailies(self):
		# Dailies
		# If we didn't find the list, we have to make a new one
		# and again assume all the Dailies were finished
		if not self.dailies_list:
			self.dailies_list = self.board.add_list('Dailies')
		# Otherwise, we check which cards haven't been finished
		else:
			self.trello_dailies = self.dailies_list.list_cards()
			# If the list was closed, we open it
			if self.dailies_list.closed:
				self.dailies_list.open()

			# Now, we iterate through all of the cards
			for daily in self.trello_dailies:
				daily.fetch(eager=True)
				# Build up a dictionary (for easy lookups later) of the trello cards
				self.dailies_dict[daily.description] = daily
				# if the trello card is not in our HabitRPG Dailies or Dailies Completed list
				# we have a new card
				if daily.description not in self.dailies:
					new_daily = self.api.create_task(HabitAPI.TYPE_DAILY, daily.name)
					print "Daily " + daily.name + " was created in Trello!"
					self.dailies[new_daily["id"]] = new_daily
					self.dailies_dict[new_daily["id"]] = new_daily
				# If the checklist item 'Complete' has been checked, the item is done!
				if daily.checklists[0].items[0]["checked"]:
					print "Daily " + daily.name + " was completed!"
					self.complete_task(self.dailies[daily.description])

		self.update_dailies()

	def update_dailies(self):
		# then we add in the cards again
		for daily_id,daily in self.dailies.items():
			if daily_id not in self.dailies_dict:
				tomorrow = date.today() + timedelta(days=1)
				midnight = datetime.combine(tomorrow, time())

				card = self.dailies_list.add_card(daily["text"], daily_id, due=str(midnight))
				daily_checked = daily["completed"]
				card.add_checklist("Complete", ["Complete"], [daily_checked])

				print "Daily " + daily["text"] + " was created in HabitRPG!"
				self.dailies_dict[daily_id] = card

	def process_habits(self):
		# Habits
		if not self.habits_list:
			self.habits_list = self.board.add_list('Habits')
		else:
			self.trello_habits = self.habits_list.list_cards()

			if self.habits_list.closed:
				self.habits_list.open()

			for trello_habit in self.trello_habits:
				trello_habit.fetch(eager=True)
				self.habits_dict[trello_habit.description] = trello_habit
				if trello_habit.description in self.habits:
					for checklist_item in trello_habit.checklists[0].items:
						if checklist_item["checked"]:
							if checklist_item["name"] == "Down":
								self.down_arrow_habit(self.habits[trello_habit.description])
							elif checklist_item["name"] == "Up":
								self.up_arrow_habit(self.habits[trello_habit.description])
						else:
							print "Nothing has changed with Habit " + trello_habit.name + "!"

				else:
					(up, down) = self.get_up_down_for(trello_habit)
					new_habit = self.api.create_habit(trello_habit.name, up, down)
					print "Habit " + trello_habit.name + " was created in Trello!"
					self.habits[new_habit["id"]] = new_habit
					self.habits_dict[new_habit["id"]] = new_habit

		self.update_habits()

	def get_up_down_for(self, trello_habit):
		up = False
		down = True
		for label in trello_habit.labels:
			if label.name == "Up":
				up = True
			else:
				up = False
			if label.name == "Down":
				down = True
			else:
				down = False
		return (up, down)

	def up_arrow_habit(self, habit):
			self.api.perform_task(habit["id"], HabitAPI.DIRECTION_UP)
			print "Habit " + habit["text"] + " was Up'd!"

	def down_arrow_habit(self, habit):
			self.api.perform_task(habit["id"], HabitAPI.DIRECTION_DOWN)
			print "Habit " + habit["text"] + " was Down'd!"

	def update_habits(self):
		for habit_id,habit in self.habits.items():
			if habit_id not in self.habits_dict:
				labels = []
				checklist_items = []
				checklist_values = []
				if habit["up"]:
					labels.append(self.get_label_for("Up"))
					checklist_items.append("Up")
					checklist_values.append(False)
				if habit["down"]:
					labels.append(self.get_label_for("Down"))
					checklist_items.append("Down")
					checklist_values.append(False)
				card = self.habits_list.add_card(habit["text"], habit_id, labels)
				card.add_checklist("Up/Down", checklist_items, checklist_values)
				print "Habit " + habit["text"] + " was created in HabitRPG!"
				self.habits_dict[habit_id] = card

	def process_todos(self):
		# Todos
		if not self.todos_list:
			self.todos_list = self.board.add_list('Todos')
		else:
			self.trello_todos = self.todos_list.list_cards()
			if self.todos_list.closed:
				self.todos_list.open()

			for trello_todo in self.trello_todos:
				trello_todo.fetch(eager=True)
				self.todos_dict[trello_todo.description] = trello_todo
				# If we have a task in Trello not in HabitRPG, it means they added it in Trello
				if trello_todo.description not in self.todos:
					new_task = self.api.create_task(HabitAPI.TYPE_TODO, trello_todo.name)
					print "Todo " + trello_todo.name + " was created in Trello!"
					self.todos[new_task["id"]] = new_task
					self.todos_dict[new_task["id"]] = new_task
				elif trello_todo.checklists[0].items[0]["checked"]:
					print "Todo " + trello_todo.name + " was finished!"
					self.complete_task(self.todos[trello_todo.description])

		self.update_todos()

	def update_todos(self):
		for todo_id,todo in self.todos.items():
			if todo_id not in self.todos_dict:
				due_date = None
				if "date" in todo:
					due_date = todo["date"]
				card = self.todos_list.add_card(todo["text"], todo_id, due=due_date)
				todo_checked = todo["completed"]
				card.add_checklist("Complete", ["Completed"], [todo_checked])
				print "Todo " + todo["text"] + " was created from HabitRPG!"
				self.todos_dict[todo_id] = card

	def complete_task(self, task):
		task["completed"] = True
		self.api.update_task(task["id"], task)

	def add_labels(self, habitrello_board):
		self.labels["Up"] = self.board.add_label("Up", "green")
		self.labels["Down"] = self.board.add_label("Down", "red")

	def get_label_for(self, label):
		if label in self.labels:
			return self.labels[label]
		return None

	def setup_board(self):
		self.board = None

		# Loop through the user's boards until we find the Habit RPG one
		for board in self.client.list_boards():
			if board.name == 'Habit RPG':
				self.board = board
				break

		# if we don't have a Habit RPG borad, then we have to make a new one
		if not self.board:
			self.board = client.add_board('Habit RPG')
			self.add_labels()
		# if the board we found was closed, then we open it
		# and assume that the user had finished all of the dailies, habits, and tasks
		elif self.board.closed:
			self.board.open()

	def setup_lists(self):
		# Now we look in the Habit RPG board for all of the lists
		for board_list in self.board.get_lists('all'):
			# if we find the Dailies list
			if board_list.name == 'Dailies':
				# We grab the object
				self.dailies_list = board_list
			# Rinse and repeat for Todos and Habits
			elif board_list.name == 'Todos':
				self.todos_list = board_list
			elif board_list.name == 'Habits':
				self.habits_list = board_list
			# Finally, we close any lists that aren't related to Habit RPG
			else:
				board_list.close()

	def get_labels(self):
		labels = self.board.get_labels()
		for label in labels:
			self.labels[label.name] = label

	def process_tasks(self):
		# Populate the separate lists
		# of habits, dailies, and todos
		for task in self.tasks:
			if task["type"] == HabitAPI.TYPE_HABIT:
				self.habits[task["id"]] = task
			elif task["type"] == HabitAPI.TYPE_TODO:
				self.todos[task["id"]] = task
			else:
				self.dailies[task["id"]] = task

	def main(self, skip_todos=False, skip_dailies=False, skip_habits=False):
		if skip_todos and skip_dailies and skip_habits:
			return
		self.process_tasks()
		self.setup_board()
		self.setup_lists()
		self.get_labels()

		if not skip_dailies:
			self.process_dailies()
		if not skip_habits:
			self.process_habits()
		if not skip_todos:
			self.process_todos()

parser = argparse.ArgumentParser(description='Sync HabitRPG and Trello tasks!')
parser.add_argument('--skip-todos', dest='skip_todos', action='store_true', help='Skip processing Todos')
parser.add_argument('--skip-dailies', dest='skip_dailies', action='store_true', help='Skip processing Dailies')
parser.add_argument('--skip-habits', dest='skip_habits', action='store_true', help='Skip processing Habits')
args = parser.parse_args()

# Get the tasks for the user in HabitRPG
api = HabitAPI(habit_uuid, habit_api_key)

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


habit = HabiTrello(api, client)
habit.main(args.skip_todos, args.skip_dailies, args.skip_habits)