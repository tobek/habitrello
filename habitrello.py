import argparse
from pyhabit import HabitAPI
from trello import *
from trello.util import *
from utils import *
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

	def process_trello_dailies(self):
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
			for trello_daily in self.trello_dailies:
				trello_daily.fetch(eager=True)
				# Build up a dictionary (for easy lookups later) of the trello cards
				self.dailies_dict[trello_daily.description] = trello_daily
				# if the trello card is not in our HabitRPG Dailies or Dailies Completed list
				# we have a new card
				if trello_daily.description not in self.dailies:
					new_daily = self.api.create_task(HabitAPI.TYPE_DAILY, trello_daily.name)
					print "Daily " + trello_daily.name + " was created in Trello!"
					self.dailies[new_daily["id"]] = new_daily
					self.dailies_dict[new_daily["id"]] = new_daily
					trello_daily.set_description(new_daily["id"])
				# If the checklist item 'Complete' has been checked, the item is done!
				if trello_checked(trello_daily):
					print "Daily " + trello_daily.name + " was completed!"
					self.complete_task(self.dailies[trello_daily.description])

		self.process_habit_dailies()

	def process_habit_dailies(self):
		# then we add in the cards again
		for daily_id,daily in self.dailies.items():
			tomorrow = get_tomorrow()
			midnight = get_midnight(tomorrow)
			if daily_id not in self.dailies_dict:

				card = self.dailies_list.add_card(daily["text"], daily_id, due=str(midnight))
				daily_checked = daily["completed"]
				card.add_checklist("Complete", ["Complete"], [daily_checked])

				print "Daily " + daily["text"] + " was created in HabitRPG!"
				self.dailies_dict[daily_id] = card

			trello_daily = self.dailies_dict[daily_id]
			daily_due = get_trello_due(trello_daily)
			if daily_due <= date.today():
				trello_daily.set_due(midnight)
				trello_daily.checklists[0].set_checklist_item("Complete", False)

	def process_trello_habits(self):
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
					trello_habit.set_description(new_habit["id"])

		self.process_habit_habits()

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

	def process_habit_habits(self):
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

	def process_trello_todos(self):
		# Todos
		# If there is no Todo list in Trello
		if not self.todos_list:
			# add it to the board
			self.todos_list = self.board.add_list('Todos')
		else:
			# otherwise, grab all of the cards
			self.trello_todos = self.todos_list.list_cards()
			# if the list is closed, open it up
			if self.todos_list.closed:
				self.todos_list.open()

			# Iterate through all of the cards in the Todo list in Trello
			for trello_todo in self.trello_todos:
				# Do an eager fetch, to get checklists
				trello_todo.fetch(eager=True)
				# Create a dictionary for looking up between HabitRPG and Trello
				self.todos_dict[trello_todo.description] = trello_todo
				# The corresponding HabitRPG Todo, assuming it doesn't exist
				habit_todo = None
				# If it does exist already, we grab it
				if trello_todo.description in self.todos:
					habit_todo = self.todos[trello_todo.description]
				# Get the due date for the Trello card
				trello_todo_due = get_trello_due(trello_todo)
				# If the due date has passed, the task is overdue!
				if trello_todo_due < date.today():
					print "Todo " + trello_todo.name + " is overdue!"
				# If we didn't already have a HabitRPG Todo for this Card
				# it was added in Trello
				if not habit_todo:
					# Create the task in HabitRPG
					habit_todo = self.api.create_task(HabitAPI.TYPE_TODO, trello_todo.name)
					# Add a Due Date to it
					habit_todo["date"] = trello_todo.due
					self.api.update_task(habit_todo["id"], habit_todo)
					print "Todo " + trello_todo.name + " was created in Trello!"
					# Add it to our Todos
					self.todos[habit_todo["id"]] = habit_todo
					self.todos_dict[habit_todo["id"]] = habit_todo
					# Make sure the trello card has the HabitRPG task ID in the description
					trello_todo.set_description(habit_todo["id"])
				else:
					# If we already have the HabitRPG task, we're sync'd Trello->HabitRPG
					# First we check to see if the task was completed in Trello
					todo_completed = False
					if trello_checked(trello_todo):
						self.complete_task(habit_todo)
						todo_completed = True
					# Now we check to see if the todo was already finished in HabitRPG
					if habit_todo["completed"]:
						trello_todo.checklists[0].set_checklist_item("Complete", True)
						todo_completed = True
					if todo_completed:
						print "Todo " + trello_todo.name + " was finished!"
					# Now we need to check if the due dates match up.
					habit_todo_due = None
					if "date" in habit_todo:
						habit_todo_due = datetime.strptime(habit_todo["date"], "%m/%d/%Y").date()
					# We will assume Trello has the correct due date.
					# Only really because there's no good way to determine, without
					# using settings (possible TODO)
					if habit_todo_due != trello_todo_due:
						habit_todo["date"] = trello_todo.date
						self.api.update_task(habit_todo)

		self.process_habit_todos()

	def process_habit_todos(self):
		for todo_id,todo in self.todos.items():
			if todo_id not in self.todos_dict and not todo["completed"]:
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
			self.process_trello_dailies()
		if not skip_habits:
			self.process_trello_habits()
		if not skip_todos:
			self.process_trello_todos()

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