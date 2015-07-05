import datetime
import time


def get_trello_due(trello_card):
	if hasattr(trello_card, "due"):
		return datetime.datetime.strptime(trello_card.due, "%Y-%m-%d").date()
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
	return trello_card.checklists[0].items[0]["checked"]


def trello_to_habit_due(trello_card_due):
	return datetime.datetime.strptime(trello_card_due, "%Y-%m-%d").strftime("%m/%d/%Y")


def habit_to_trello_due(habit_task_due):
	if "T" in habit_task_due:
		habit_task_due = habit_task_due.split("T")[0]
	if "/" in habit_task_due:
		return datetime.datetime.strptime(habit_task_due, "%m/%d/%Y").stftime("%Y-%m-%d")
	else:
		return habit_task_due


def now():
	ts = time.time()
	return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def print_message(message):
	print now() + " - " + message


def get_up_down_for(trello_habit):
	up = False
	down = True
	for label in trello_habit.labels:
		if label["name"] == "Up":
			up = True
		else:
			up = False
		if label["name"] == "Down":
			down = True
		else:
			down = False
	return (up, down)
	