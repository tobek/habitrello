class Task(object):
	def __init__(self, api):
		self.api = api
		self.tasks = {}

	def add(self, task):
		self.tasks[task["id"]] = task

	def complete_task(self, task):
		task["completed"] = True
		self.api.update_task(task["id"], task)
