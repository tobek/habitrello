from pyhabit import HabitAPI
from habitrello.task import Task
from habitrello.utils import print_message,	get_up_down_for

class Habits(Task):
	def __init__(self, api, client):
		super(Habits, self).__init__(api, client)
		self.habits = {}
		self.list = None
		self.labels = {}

	def process_trello(self):
		if self.list is None:
			print_message('No Habits to process.')
			return
		# Habits
		for trello_habit in self.list.list_cards():
			trello_habit.fetch(eager=True)
			self.habits[trello_habit.description] = trello_habit
			if trello_habit.description in self.tasks:
				try:  # Catch exception if there is no checkllist
					for checklist_item in trello_habit.checklists[0].items:
						if checklist_item["checked"]:
							if checklist_item["name"] == "Down":
								self.arrow_habit(self.habits[trello_habit.description], HabitAPI.DIRECTION_DOWN)
							elif checklist_item["name"] == "Up":
								self.arrow_habit(self.habits[trello_habit.description], HabitAPI.DIRECTION_UP)
						else:
							print_message("Nothing has changed with Habit " + trello_habit.name + "!")
				except AttributeError:
					continue

			else:
				(is_up, is_down) = get_up_down_for(trello_habit)
				new_habit = self.api.create_habit(trello_habit.name, is_up, is_down)
				print_message("Habit " + trello_habit.name + " was created in Trello!")
				self.habits[new_habit["id"]] = new_habit
				self.tasks[new_habit["id"]] = new_habit
				trello_habit.set_description(new_habit["id"])
		print_message("Done!")

	def arrow_habit(self, habit, direction):
		self.api.perform_task(habit["id"], direction)
		print_message("Habit " + habit["text"] + " was " + direction + "'d!")

	def process_habit(self):
		for habit_id, habit in self.tasks.items():
			if habit_id not in self.habits:
				labels, checklist_items, checklist_values = self.get_habit_checklist_label(habit)
				card = self.list.add_card(habit["text"], habit_id, labels)
				card.add_checklist("Up/Down", checklist_items, checklist_values)
				print_message("Habit " + habit["text"] + " was created in HabitRPG!")
				self.habits[habit_id] = card
		print_message("Done!")

	def get_label_for(self, label):
		return self.labels.get(label, None)

	def get_habit_checklist_label(self, habit):
		labels = []
		checklist_items = []
		checklist_values = []
		for prop, label in [["up", "Up"], ["down", "Down"]]:
			if habit[prop]:
				labels.append(self.get_label_for(label))
				checklist_items.append(label)
				checklist_values.append(False)
		return labels, checklist_items, checklist_values
