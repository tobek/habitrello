class Tasks(object):
	def __init__(self, api, skip=False):
		self.api = api
		self.tasks = {}
		self.list = None
		self.skip = skip

	def add(self, task):
		self.tasks[task["id"]] = task

	def complete_task(self, task):
		task["completed"] = True
		self.api.update_task(task["id"], task)

	def process_trello(self):
		pass

	def process_habit(self):
		pass

	def process(self):
		if self.skip:
			return
		self.process_trello()
		self.process_habit()
