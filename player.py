import os
import wave
import time
import threading
import logging

import alsaaudio as aa

logger = logging.getLogger()

class Player(object):
	"""
	Threaded class that plays a wav file
	"""
	def __init__(self, path=None):
		"""

		"""
		logger.debug("initalizing player with sound: %s" % path)

		# do some more error checking
		# like if the player tries to play without a
		# song initalized

		self._periodsize = 1024 # 8192
		
		if path != None:
			self.load(path)

	def load(self, path):
		"""

		"""
		logger.debug("loading player with sound: %s" % path)

		p = os.path.abspath(path)

		self.playing = False
		self._w = wave.open(p)

		self._player = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
		self._player.setchannels(self._w.getnchannels())
		self._player.setrate(self._w.getframerate())
		self._player.setformat(aa.PCM_FORMAT_S16_LE)
		self._player.setperiodsize(self._periodsize)

		self._t = threading.Thread(target=self._run)

	def play(self, end_delay=0, join=True):
		"""

		"""
		logger.debug("starting player thread")

		self.playing = True
		self._end_delay = end_delay
		self._data = self._w.readframes(self._periodsize)

		self._t.start()

		if join:
			self._t.join()

	def _run(self):
		"""

		"""
		while self._data != '' and self.playing:
			self._player.write(self._data)
			self._data = self._w.readframes(self._periodsize)

		self.playing = False

		time.sleep(self._end_delay)

		logger.debug("player thread stopped")
