#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
	Fancy title or something
"""

import logging
import urllib2
import datetime, time
import thread, threading, subprocess

import alsaaudio as aa
import wave, os, sys, json
from pydub import AudioSegment

# setup all the logger stuff

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if os.path.isfile(os.path.abspath("log.txt")):
	os.remove(os.path.abspath("log.txt"))

handler = logging.FileHandler("log.txt")
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s: [%(funcName)s]: %(message)s')
handler.setFormatter(formatter)

#stream_handle = logging.StreamHandler()
#stream_handle.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())


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

class AlarmPool(object):
	"""

	"""
	def __init__(self):
		"""

		"""
		self.alarm_file = "alarms.json"
		self.log_file = "log.txt"
		self.next_pending = None
		self.running = True
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

		"""
		for a in self.pool:
			if a.name == name:
				return a

	def debug(self):
		logger.debug("alarm went off because of debuggingggg")
		self.select_next_pending()
		self.next_pending.prepare()
		self.next_pending.set_off()


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


def convert_mp3(filename, output_name):
	"""

	"""
	if os.path.isfile("ffmpeg.exe"):
		ffmpeg = "ffmpeg.exe" # windows
	else:
		ffmpeg = "ffmpeg" # linux

	path = os.path.abspath(filename)
	out = os.path.abspath(output_name)

	command = [ ffmpeg,
		"-i", path, # input path
		"-y", # overwrite without prompt
		out # output path
	]

	pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)
	
	ret = pipe.wait()
	name = os.path.basename(filename)
	name_out = os.path.basename(output_name)

	if ret != 0:
		logger.error("FFmpeg returned code (%d) converting file '%s' -> '%s" % (ret, name, name_out))
		return False
	
	logger.info("FFmpeg returned code (%d) converting file '%s' -> '%s'" % (ret, name, name_out))
	return True

def get_date():
	"""

	"""
	return datetime.datetime.now()

def get_time():
	"""

	"""
	return datetime.datetime.time(get_date())


def main():
	"""
	Main or something
	"""

	logger.info("script starting up @ %s" % str(get_date()))

	try:
		Alarm.set_volume(90)

		#name = "file1.mp3"
		#q = "Good morning Syntox!. Today's weather is quite nice. This sentence is about to be over a hundred characters long and this is not good for the tts thing because it will truncate it" 
		#q = "Good morning Henning!. What the fuck are you talking about? Why is this not working"
		#q = "Good morning Syntox!. Todays weather is quite nice" 

		#q1 = "This is one query This is one query This is one query This is one query This is one query This is one query"
		#q2 = "This is a second query"
		#q3 = "This is a third query"

		#p1 = Player("music/fivehours.wav")
		#p2 = Player("query/query-1.wav")

		#qh = QueryHandler()
		#qh.load([q1, q2, q3])

		#p2.play(0, False)
		#p1.play(0, False)

		#time.sleep(1)

		#qh.play(1)

		pool = AlarmPool()
		pool.load()
		#pool.debug()
		pool.run()

	except KeyboardInterrupt:
		logger.exception("keyboard interrupt")

	except:
		logger.exception("exception occured")
		raise

	logger.info("script finishing up @ %s" % str(get_date()))

if __name__ == "__main__":
        main()