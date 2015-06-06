import os
import time
import datetime
import subprocess
import logging

from os.path import *
from pydub import AudioSegment

logger = logging.getLogger()

def convert_mp3(filename, overwrite=False):
	"""
	Convert a .mp3 file into a .mp3 file using pydub

	Overwrite True will convert the file even if the file exists
	"""
	in_path = abspath(filename)
	out_path = abspath(splitext(filename)[0]) + ".wav"

	logger.debug("converting file .mp3 to .wav:")
	logger.debug(" <- %s" % in_path)
	logger.debug(" -> %s" % out_path)

	if not isfile(out_path) or overwrite:
		AudioSegment.from_file(in_path).export(out_path, format="wav")
		logger.debug("conversion completed successfully...")
	else:
		logger.debug("file already exist.. skipping convertion..")

	return out_path

def get_date():
	"""
	Get the current datetime
	"""
	return datetime.datetime.now()

def get_time():
	"""
	Get the current time
	"""
	return datetime.datetime.time(get_date())
