import os
import urllib2

from alarm.player import Player
from alarm.logger import logger
from alarm.utils import convert_mp3

class QueryHandler(object):
	"""
	QueryHandler object for handling downloading, conversion
	and plyaing of queries.
	"""
	def __init__(self):
		"""
		Initializes a QueryHandler object
		"""
		self.loaded = False

	def load(self, q_list):
		"""
		Takes a given list of queries in a string format
		and converts them into wav files which can be played later.
		"""
		logger.debug("loaded query handler")

		self.sound_list = self._queue_queries(q_list)
		self.loaded = True

	def play(self, delay=0):
		"""
		Plays a prepared list of queries.
		"""
		logger.info("playing query list...")

		if not self.loaded:
			logger.warning("the query handler must be loaded to continue")
			return

		self._play_queries(delay, self.sound_list)

		logger.debug("played queries successfully...")

	def _query(self, text):
		"""
		Escape a given string for use as an URL.
		"""
		return urllib2.quote(text)

	def _play_queries(self, delay, sounds):
		"""
		Itterates over a given list of queries and plays them
		with a given delay after each one.
		"""
		logger.debug("playing query queue...")

		p = Player()
		idx = 0
		maxidx = len(sounds)

		while idx < maxidx:
			p.load(sounds[idx])
			logger.debug("playing and then delaying for %d seconds..." % delay)
			
			p.play(delay, True)
			idx += 1

		logger.debug("played queue successfully...")

	def _queue_queries(self, queries):
		"""
		Retrieves and converts a list of queries 
		and returns a list of the paths to the converted .wav files.
		"""
		sounds = []
		
		for i, q in enumerate(queries):
			template = "query/query-%d.%s"
			name = template % (i, "mp3")
			ret = self._get_query(name, q)

			if ret:
				wav = convert_mp3(name, True)
				sounds.append(wav)

				logger.info("queued up sound: %s" % wav)
				logger.debug(wav)
			else:
				logger.warning("failed to retreieve query: %s" % wav)

		return sounds

	def _get_query(self, save_name, text):
		"""
		Takes a given string and converts it into a .mp3 file,
		which can later be converted.
		"""
		try:
			li = text.split(" ")
			q = []
			maxlen = 100
			index = 0

			with open(save_name, "wb") as f:
				for i, w in enumerate(li):
					neww = w + " "
					newlist = list(q)
					newlist.append(neww)
					newlen = len(" ".join(newlist))

					if newlen >= maxlen:
						s = " ".join(q)
						logger.debug("query string: %s" % s)

						r = self._request_query(s, index)
						f.write(r)

						index += 1
						q = []
						q.append(w)
					else:
						q.append(neww)

				s = " ".join(q)
				logger.debug("query string: %s" % s)

				r = self._request_query(s, index)
				f.write(r)

			logger.info("successfully retrieved query translation...")
			return True

		except IOError as e:
			err = str(e)
			logger.error("ioerror saving query: %s" % err)

			return False

	def _request_query(self, text, index):
		"""
		Requests a query to the google translate API and 
		returns the .mp3 data. 
		"""
		try:
			q = self._query(text)
			l = len(text)

			url = "http://translate.google.com/translate_tts?tl=en&q=%s&total=%s&idx=%s&client=t&prev=input" % (q, l, index)
			logger.info("query reqeust url: %s" % url)

			# headers taken from https://github.com/hungtruong/Google-Translate-TTS
			headers = {
				"Host": "translate.google.com",
				"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) "
					"AppleWebKit/535.19 (KHTML, like Gecko) "
					"Chrome/18.0.1025.163 Safari/535.19"
			}
			
			req = urllib2.Request(url, "", headers)
			resp = urllib2.urlopen(req)

			return resp.read()

		except urllib2.HTTPError as e:
			logger.error("http error requesting query(index: %s): %s" % (str(index), str(e)))
			return None
