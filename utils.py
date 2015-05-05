from datetime import date, time, timedelta, datetime
def get_trello_due(trello_card):
	if hasattr(trello_card, "due"):
		return datetime.strptime(trello_card.due, "%Y-%m-%d").date()
	else:
		trello_card.due = date.today().strftime("%Y-%m-%d")
		return date.today()

def get_habit_due(task):
	if "date" in task:
		return datetime.strptime(task["date"], "%m/%d/%Y").date()
	else
		return date.today().strftime("%m/%d/%Y").date()

def get_tomorrow():
	return date.today() + timedelta(days=1)

def get_midnight(day):
	return datetime.combine(day, time())

def trello_checked(trello_card):
	return trello_card.checklists[0].items[0]["checked"]

def trello_to_habit_due(trello_card_due):
	return trello_card_due.stftime("%m/%d/%Y")