import datetime
import time


def get_trello_due(trello_card):
	if hasattr(trello_card, "due"):
		return datetime.datetime.strptime(trello_card.due.split("T")[0], "%Y-%m-%d").date()
	else:
		trello_card.due = datetime.date.today().strftime("%Y-%m-%d")
		return datetime.date.today()


def get_habit_due(task):
	if "date" in task:
		if "T" in task["date"]:
			task["date"] = task["date"].split("T")[0]
		if "/" in task["date"]:
			return datetime.datetime.strptime(task["date"], "%m/%d/%Y").date()
		else:
			return datetime.datetime.strptime(task["date"], "%Y-%m-%d").date()
	else:
		return None


def get_tomorrow():
	return datetime.date.today() + datetime.timedelta(days=1)


def get_midnight(day):
	return datetime.datetime.combine(day, datetime.time())


def trello_checked(trello_card):
	HABIT_CHECKLIST_NAME = 'Complete' # Should maybe be different and/or in some config

	habit_checklist = None
	try:
		for checklist in trello_card.checklists:
			if checklist.name == HABIT_CHECKLIST_NAME:
				habit_checklist = checklist
	except (AttributeError, IndexError):
		return False

	if not habit_checklist:
		return False

	try:
		item = habit_checklist.items[0]
	except (AttributeError, IndexError):
		return False

	return item["checked"]


def trello_to_habit_due(trello_card_due):
	return datetime.datetime.strptime(trello_card_due.split("T")[0], "%Y-%m-%d").strftime("%m/%d/%Y")


def habit_to_trello_due(habit_task_due):
	if "T" in habit_task_due:
		habit_task_due = habit_task_due.split("T")[0]
	if "/" in habit_task_due:
		return datetime.datetime.strptime(habit_task_due, "%m/%d/%Y").strftime("%Y-%m-%d")
	else:
		return habit_task_due


def now():
	timestamp = time.time()
	return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def print_message(message):
	print "%s - %s" % (now(), message)


def get_up_down_for(trello_habit):
	is_up = False
	is_down = False
	try:
		for label in trello_habit.labels:
			if label.name == "Up":
				is_up = True
			if label.name == "Down":
				is_down = True
	except AttributeError:
		pass
	return (is_up, is_down)
