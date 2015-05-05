from datetime import date, time, timedelta, datetime
def get_trello_due(trello_card):
	if hasattr(trello_card, "due"):
		return datetime.strptime(trello_card.due, "%Y-%m-%d").date()
	else:
		trello_card.due = date.today().strftime("%Y-%m-%d")
		return date.today()

def get_tomorrow():
	return date.today() + timedelta(days=1)

def get_midnight(day):
	return datetime.combine(day, time())

def trello_checked(trello_card):
	return trello_card.checklists[0].items[0]["checked"]