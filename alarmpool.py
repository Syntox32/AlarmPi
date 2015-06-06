import os
import sys
import json
import time
import logging

from alarmobject import Alarm
from utils import *

logger = logging.getLogger()

class AlarmPool(object):
	"""
	Class for handling all the alarm object.
	"""
	def __init__(self):
		"""
		Initialize an instance of an AlarmPool
		"""
		self.alarm_file = "alarms.json"
		self.log_file = "alarm.log"
		self.next_pending = None
		self.pool = []
		self.pre_wake_time = 30 # seconds

	def load(self):
		"""
		Loads the alarms, duuh
		"""
		if os.path.isfile(os.path.abspath(self.alarm_file)):
			logger.debug("alarms.json found...")
		else:
			logger.critical("could not find alarms.json... exiting")
			sys.exit(1)

		path = os.path.abspath(self.alarm_file)
		with open(path, "r") as f:
			json_data = f.read()

		alarm_json = json.loads(json_data)
		al = []

		for k in alarm_json:
			o = alarm_json[k]
			a = Alarm(k,
				o["label"],
				int(o["hour"]),
				int(o["minute"]),
				o["days"],
				o["options"])
			al.append(a)
		self.pool = al

		logger.debug("loaded %d alarms..." % len(self.pool))

	def select_next_pending(self):
		"""
		Select and set the next pending alarm.
		"""
		if not (len(self.pool) > 0):
			logger.warning("found no alarms... exiting")
			sys.exit(1)

		date = get_date()
		lowest = self.pool[0]

		for alarm in self.pool:
			if alarm.time_pending() < lowest.time_pending() and alarm.time_pending() > date:
				lowest = alarm

		logger.info("next pending alarm (%s) @%s" % (lowest.name, str(lowest.time_pending())))
		self.next_pending = lowest
		return lowest

	def run(self):
		"""
		Start the main loop.
		"""
		self.select_next_pending()
		delta_t = self.next_pending.time_pending() - get_date()
		sec_to_next = delta_t.total_seconds()
		sleep_time = sec_to_next - self.pre_wake_time

		if sec_to_next >= self.pre_wake_time:
			logger.info("Sleeping for %d seconds..." % sleep_time)
			time.sleep(sec_to_next - self.pre_wake_time)

		logger.info("alarm going of in %d seconds... preparing..." % self.pre_wake_time)
		
		# prepare the alarm and shit
		self.next_pending.prepare()
		logger.debug("waiting...")
		while self.next_pending.time_pending() > get_date():
			time.sleep(1)

		logger.info("pling pling pling")
		self.next_pending.set_off()

	def _alarm_from_name(self, name):
		"""
		Private function to get an alarm by it's name.
		"""
		for a in self.pool:
			if a.name == name:
				return a

	def debug(self):
		"""
		Woo debugging
		"""
		logger.debug("alarm went off because of debuggingggg")
		self.select_next_pending()
		self.next_pending.prepare()
		self.next_pending.set_off()
