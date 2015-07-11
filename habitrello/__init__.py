'''
__init__.py

This stores the HabiTrello class that does all of the heavy lifting to
sync HabitRPG and Trello.
'''
from pyhabit import HabitAPI
from habitrello.utils import get_trello_due, get_habit_due, get_tomorrow, print_message,\
	get_midnight, trello_checked, trello_to_habit_due, habit_to_trello_due,\
	get_up_down_for
from habitrello.settings import board_name, todos_list_name,\
	dailies_list_name, habits_list_name, close_other_lists
from datetime import date
from habitrello.habits import Habits
from habitrello.todos import Todos
from habitrello.dailies import Dailies
from multiprocessing import Process


class HabiTrello(object):
	'''
	The HabiTrello client used for syncing HabitRPG and Trello.
	'''
	def __init__(self, api, client, args):
		self.api = api
		self.client = client
		self.tasks = api.tasks()
		self.labels = {}
		self.board = None
		self.habits = Habits(api, args.skip_habits)
		self.dailies = Dailies(api, args.skip_dailies)
		self.todos = Todos(api, args.skip_todos)
		self.setup_board()
		self.setup_lists()
		self.get_labels()
		self.habits.labels = self.labels

	def add_labels(self):
		self.labels["Up"] = self.board.add_label("Up", "green")
		self.labels["Down"] = self.board.add_label("Down", "red")

	def setup_board(self):
		# Loop through the user's boards until we find the Habit RPG one
		for board in self.client.list_boards():
			if board.name == board_name:
				self.board = board
				break

		# if we don't have a Habit RPG borad, then we have to make a new one
		if self.board is None:
			self.board = self.client.add_board(board_name)
			self.add_labels()
		# if the board we found was closed, then we open it
		# and assume that the user had finished all of the dailies, habits, and tasks
		elif self.board.closed:
			self.board.open()

	def setup_lists(self):
		# Now we look in the Habit RPG board for all of the lists
		for board_list in self.board.get_lists('all'):
			# if we find the Dailies list
			if board_list.name == dailies_list_name:
				# We grab the object
				self.dailies.list = board_list
			# Rinse and repeat for Todos and Habits
			elif board_list.name == todos_list_name:
				self.todos.list = board_list
			elif board_list.name == habits_list_name:
				self.habits.list = board_list
			# Finally, we close any lists that aren't related to Habit RPG
			else:
				if close_other_lists:
					board_list.close()

		self.todos.list = self.setup_list(self.todos.list, todos_list_name)
		self.habits.list = self.setup_list(self.habits.list, habits_list_name)
		self.dailies.list = self.setup_list(self.dailies.list, dailies_list_name)

	def setup_list(self, trello_list, name):
		if trello_list is None:
			trello_list = self.board.add_list(name)
		if trello_list.closed:
			trello_list.open()
		return trello_list

	def get_labels(self):
		labels = self.board.get_labels()
		for label in labels:
			self.labels[label.name] = label

	def process_tasks(self):
		# Populate the separate lists
		# of habits, dailies, and todos
		for task in self.tasks:
			if task["type"] == HabitAPI.TYPE_HABIT:
				self.habits.add(task)
			elif task["type"] == HabitAPI.TYPE_TODO:
				self.todos.add(task)
			else:
				self.dailies.add(task)

	def main(self, skip_todos=False, skip_dailies=False, skip_habits=False):
		if skip_todos and skip_dailies and skip_habits:
			return
		self.process_tasks()

		dailies_proc = Process(target=self.dailies.process)
		dailies_proc.start()
		habits_proc = Process(target=self.habits.process)
		habits_proc.start()
		todos_proc = Process(target=self.todos.process)
		todos_proc.start()

		dailies_proc.join()
		habits_proc.join()
		todos_proc.join()
