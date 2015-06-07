import os
import time
import datetime

import alsaaudio as aa
from pydub import AudioSegment

from alarm.queryhandler import QueryHandler
from alarm.player import Player
from alarm.soundloader import Soundloader
from alarm.logger import logger
from alarm.utils import *

class Alarm(object):
	"""
	An Alarm object holds an instance for a single alarm,
	this class is used to prepare, load and set-off an alarm.
	"""
	def __init__(self, name, label, hour, minute, days, options):
		"""
		Initializes an Alarm object using a given time and option.
		"""
		self.name = name
		self.label = label
		self.hour = hour
		self.minute = minute
		self.days = days
		self.options = options
		self.prepared = False

		# Soundcloud instance
		self.sc = None

		# default fallback incase we can't fetch
		# the song from soundcloud
		self.default_fallback = os.path.abspath("music/sandstorm.wav")

	def delta(self):
		"""
		Returns the Alarm time as a timedelta object.
		"""
		return datetime.timedelta(hours=self.hour, minutes=self.minute)

	def time_pending(self):
		"""
		Returns the date and time for the next time the alarm is set to go off.
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
		#p = os.path.abspath("music/uptown-funk.mp3")
		#p2 = os.path.abspath("music/uptown-funk.wav")
		p = os.path.abspath("music/higher-love.mp3")
		# p2 = os.path.abspath("music/higher-love.wav")
		
		

		# returns the song path even if the file exists
		song_path = convert_mp3(p)
		
		return song_path

	def prepare(self):
		"""
		Prepares an alarm before it is set off.
		Queries and music is downloaded, converted and prepared, this usually
		takes around 15 to 30 seconds.
		"""
		self.mp = Player()
		self.qh = QueryHandler()
		self.sc = Soundloader()

		# temp
		# weather goes here
		q = [ "Fuck you faggot, have a nice day.",
			"Today has a 97 percent chance of raining.",
			"Good morning." ]

		self.qh.load(q)

		self.query_delay = 1
		self.query_start_delay = 4
		self.query_db_sink = 10
		self.query_duration = self._get_query_duration(self.qh.sound_list)

		logger.info("query duration: %d seconds" % self.query_duration)

		song_path = self.get_song()
		new_song_path = self._prepare_segment_fade(song_path)
		self.mp.load(new_song_path)

		self.prepared = True

	def set_off(self):
		"""
		Set's off the alarm.
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
		Prepares music by fading/damping a portion of it so you can better
		hear the queries as they are played asynchronously.
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
			to_gain=gain + 2.5,
			start=int(end_s - fade_s),
			end=int(end_s))

		path = wav_path + "-edit.wav"
		seg2.export(wav_path + "-edit.wav", format="wav")
		return path

	def _get_query_duration(self, q_list):
		"""
		Returns the length of a query list.
		"""
		duration = 0

		for q in q_list:
			seg = AudioSegment.from_file(q, format="wav")
			duration += (seg.duration_seconds + self.query_delay)

		return duration

	@staticmethod
	def set_volume(percent):
		"""
		Set's the volume of system, duuh.
		"""
		mixer = aa.Mixer(control='PCM')
		mixer.setvolume(percent)
		
		volume = mixer.getvolume()
		logger.info("volume set to: %s" % str(volume))

		return volume
		