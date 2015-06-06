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
		Initialize a player object, either with or without a path.

		If it is not initalized with a path you have to use the load function
		to manually load object with a file. 
		"""
		logger.debug("initalizing player with sound: %s" % path)

		# with concurrent streams you will experience
		# stuttering if the periodsize is too big
		self._periodsize = 1024 # 8192
		
		if path != None:
			self.load(path)

	def load(self, path):
		"""
		Loads a uncompressed music file into the object.

		This can be called as many times as you would like
		during the lifetime of the object, as long as the previous
		file has finished playing.
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
		Play a loaded file.

		'end_delay' is the number of seconds to wait before actually finishing playing.
		
		If 'join' is true the main thread will wait for this one to
		finish before moving along.
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
		Private function that plays the loaded uncompressed file.
		"""
		while self._data != '' and self.playing:
			self._player.write(self._data)
			self._data = self._w.readframes(self._periodsize)

		self.playing = False

		time.sleep(self._end_delay)

		logger.debug("player thread stopped")
