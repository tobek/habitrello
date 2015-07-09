from pyhabit import HabitAPI
from habitrello.task import Task
from habitrello.utils import get_trello_due, get_tomorrow, print_message,\
	get_midnight, trello_checked
from datetime import date

class Dailies(Task):
	def __init__(self, api, client):
		super(Dailies, self).__init__(api, client)
		self.dailies = {}
		self.list = None

	def process_trello(self):
		if self.list is None:
			print_message('No Dailies to process.')
			return

		# Dailies
		# Now, we iterate through all of the cards
		for trello_daily in self.list.list_cards():
			trello_daily.fetch(eager=True)
			# Build up a dictionary (for easy lookups later) of the trello cards
			self.dailies[trello_daily.description] = trello_daily
			# if the trello card is not in our HabitRPG Dailies or Dailies Completed list
			# we have a new card
			if trello_daily.description not in self.tasks:
				new_daily = self.api.create_task(HabitAPI.TYPE_DAILY, trello_daily.name)
				print_message("Daily " + trello_daily.name + " was created in Trello!")
				self.dailies[new_daily["id"]] = new_daily
				self.tasks[new_daily["id"]] = new_daily
				trello_daily.set_description(new_daily["id"])
			# If the checklist item 'Complete' has been checked, the item is done!
			if trello_checked(trello_daily):
				print_message("Daily " + trello_daily.name + " was completed!")
				self.complete_task(self.dailies[trello_daily.description])

	def process_habit(self):
		# then we add in the cards again
		for daily_id, daily in self.tasks.items():
			tomorrow = get_tomorrow()
			midnight = get_midnight(tomorrow)
			if daily_id not in self.dailies:

				card = self.list.add_card(daily["text"], daily_id, due=str(midnight))
				daily_checked = daily["completed"]
				card.add_checklist("Complete", ["Complete"], [daily_checked])

				print_message("Daily " + daily["text"] + " was created in HabitRPG!")
				self.dailies[daily_id] = card

			trello_daily = self.dailies[daily_id]
			daily_due = get_trello_due(trello_daily)
			if daily_due <= date.today():
				trello_daily.set_due(midnight)
				trello_daily.checklists[0].set_checklist_item("Complete", False)
