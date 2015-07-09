from pyhabit import HabitAPI
from habitrello.task import Task
from habitrello.utils import get_trello_due, get_habit_due, print_message,\
	trello_checked, trello_to_habit_due, habit_to_trello_due
from datetime import date

class Todos(Task):
	def __init__(self, api):
		super(Todos, self).__init__(api)
		self.todos = {}

	def process_trello(self):
		print_message("Processing Trello Todos.")
		if self.list is None:
			print_message('No Todos to process.')
			return
		# Todos
		# Iterate through all of the cards in the Todo list in Trello
		for trello_todo in self.list.list_cards():
			# Do an eager fetch, to get checklists
			trello_todo.fetch(eager=True)
			# Create a dictionary for looking up between HabitRPG and Trello
			self.todos[trello_todo.description] = trello_todo
			# The corresponding HabitRPG Todo, assuming it doesn't exist
			habit_todo = None
			# If it does exist already, we grab it
			if trello_todo.description in self.tasks.keys():
				habit_todo = self.tasks[trello_todo.description]
			# Get the due date for the Trello card
			trello_todo_due = get_trello_due(trello_todo)
			# If the due date has passed, the task is overdue!
			if trello_todo_due < date.today():
				print_message("Todo " + trello_todo.name + " is overdue!")
			# If we didn't already have a HabitRPG Todo for this Card
			# it was added in Trello
			if habit_todo is None:
				# Create the task in HabitRPG
				habit_todo = self.api.create_task(HabitAPI.TYPE_TODO, trello_todo.name)
				# Add a Due Date to it
				habit_todo["date"] = trello_to_habit_due(trello_todo.due)
				self.api.update_task(habit_todo["id"], habit_todo)
				print_message("Todo " + trello_todo.name + " was created in Trello!")
				# Add it to our Todos
				self.todos[habit_todo["id"]] = habit_todo
				self.tasks[habit_todo["id"]] = habit_todo
				# Make sure the trello card has the HabitRPG task ID in the description
				trello_todo.set_description(habit_todo["id"])
			else:
				# If we already have the HabitRPG task, we're sync'd Trello->HabitRPG
				self.check_completed(habit_todo, trello_todo)
				# Now we need to check if the due dates match up.
				habit_todo_due = get_habit_due(habit_todo)
				# We will assume Trello has the correct due date.
				# Only really because there's no good way to determine which to use
				# without using settings (possible TODO)
				if habit_todo_due != trello_todo_due:
					habit_todo["date"] = trello_to_habit_due(trello_todo.due)
					self.api.update_task(habit_todo["id"], habit_todo)
		print_message("Done!")

	def check_completed(self, habit_todo, trello_todo):
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
				print_message("Todo " + trello_todo.name + " was finished!")

	def process_habit(self):
		print_message("Processing HabitRPG Todos.")
		for todo_id, todo in self.tasks.items():
			if todo_id not in self.todos and not todo["completed"]:
				due_date = None
				if "date" in todo:
					due_date = habit_to_trello_due(todo["date"])
				card = self.list.add_card(todo["text"], todo_id, due=due_date)
				todo_checked = todo["completed"]
				card.add_checklist("Complete", ["Completed"], [todo_checked])
				print_message("Todo " + todo["text"] + " was created from HabitRPG!")
				self.todos[todo_id] = card
		print_message("Done!")
