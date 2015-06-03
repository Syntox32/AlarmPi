import os
import time
import datetime
import logging

import alsaaudio as aa
from pydub import AudioSegment
from queryhandler import QueryHandler
from player import Player
from utils import *

logger = logging.getLogger()

class Alarm(object):
	"""
	Alarm object to hold all the things
	"""
	def __init__(self, name, label, hour, minute, days, options):
		"""

		"""
		self.name = name
		self.label = label
		self.hour = hour
		self.minute = minute
		self.days = days
		self.options = options
		self.prepared = False

	def delta(self):
		"""

		"""
		return datetime.timedelta(hours=self.hour, minutes=self.minute)

	def time_pending(self):
		"""

		"""
		now = datetime.datetime.now()
		within_the_hour = self.hour == now.hour and now.minute >= self.minute
		yet_to_happend = self.hour >= now.hour

		if yet_to_happend or within_the_hour:
			# today
			date = datetime.datetime(now.year,
				now.month,
				now.day,
				self.hour,
				self.minute,
				0, 0, now.tzinfo)
		else:
			# tomorrow
			d = now + datetime.timedelta(days=1)
			date = datetime.datetime(d.year,
				d.month,
				d.day,
				self.hour,
				self.minute,
				0, 0, d.tzinfo)
		return date

	def get_song(self):
		"""
		Will extend to choose from a custom filter set by options

		..or something

		also do some smart things with the converting
		"""
		p = os.path.abspath("music/uptown-funk.mp3")
		p2 = os.path.abspath("music/uptown-funk.wav")
		
		if not os.path.isfile(p2):
			convert_mp3(p, p2)
		
		return p2

	def prepare(self):
		"""

		"""
		self.mp = Player()
		self.qh = QueryHandler()

		# temp
		# weather goes here
		q = [ "This is the first test",
			"It's going to be good",
			"Good morning Syntox, it's time to kick ass." ]

		self.qh.load(q)

		self.query_delay = 1
		self.query_start_delay = 2
		self.query_db_sink = 10
		self.query_duration = self._get_query_duration(self.qh.sound_list)

		logger.info("query duration: %d seconds" % self.query_duration)

		song_path = self.get_song()
		new_song_path = self._prepare_segment_fade(song_path)
		self.mp.load(new_song_path)

		self.prepared = True

	def set_off(self):
		"""

		"""
		if not self.prepared:
			logger.warning("alarm is not prepared... default fallback...")
			# play darude sandstorm

		logger.info("alarm '%s' going off @ %s" % (self.name, get_time()))

		self.mp.play(0, False)
		time.sleep(self.query_start_delay)
		self.qh.play(self.query_delay)

		self.prepared = False

	def _prepare_segment_fade(self, wav_path):
		"""

		"""
		seg = AudioSegment.from_file(wav_path, format="wav")

		fade_s = int(1 * 500)
		gain = self.query_db_sink
		start_s = int(self.query_start_delay * 1000)
		end_s = int(start_s + (self.query_duration * 1000))

		seg1 = seg.fade(
			to_gain=-gain,
			start=start_s,
			end=int(start_s + fade_s))

		seg2 = seg1.fade(
			to_gain=gain + 5.0,
			start=int(end_s - fade_s),
			end=int(end_s))

		path = wav_path + "-edit.wav"
		seg2.export(wav_path + "-edit.wav", format="wav")
		return path

	def _get_query_duration(self, q_list):
		"""

		"""
		duration = 0

		for q in q_list:
			seg = AudioSegment.from_file(q, format="wav")
			duration += (seg.duration_seconds + self.query_delay)

		return duration

	@staticmethod
	def set_volume(percent):
		"""

		"""
		mixer = aa.Mixer(control='PCM')
		mixer.setvolume(percent)
		
		volume = mixer.getvolume()
		logger.info("volume set to: %s" % str(volume))

		return volume
		