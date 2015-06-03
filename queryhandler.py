import os
import urllib2
import logging

from player import Player
from utils import convert_mp3

logger = logging.getLogger()

class QueryHandler(object):
	"""

	"""
	def __init__(self):
		"""

		"""
		self.loaded = False

	def load(self, q_list):
		"""

		"""
		logger.debug("loaded query handler")

		self.sound_list = self._queue_queries(q_list)
		self.loaded = True

	def play(self, delay=0):
		"""

		"""
		logger.info("playing query list...")

		if not self.loaded:
			logger.warning("the query handler must be loaded to continue")
			return

		self._play_queries(delay, self.sound_list)

		logger.debug("played queries successfully...")

	def _query(self, text):
		"""

		"""
		return urllib2.quote(text)

	def _play_queries(self, delay, sounds):
		"""

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

		"""
		sounds = []
		
		for i, q in enumerate(queries):
			template = "query/query-%d.%s"
			name = template % (i, "mp3")
			ret = self._get_query(name, q)

			if ret:
				wav = template % (i, "wav")
				if not convert_mp3(name, wav):
					logger.warning("failed to convert query: %s" % wav)
					continue

				path = os.path.abspath(wav)
				sounds.append(path)

				logger.info("queued up sound: %s" % wav)
				logger.debug(path)
			else:
				logger.warning("failed to retreieve query: %s" % wav)

		return sounds

	def _get_query(self, save_name, text):
		"""

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
