import os
import time
import datetime
import subprocess
import logging

logger = logging.getLogger()

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
