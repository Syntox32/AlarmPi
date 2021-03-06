import os
import logging

"""
Initalize a logger object.

TODO: turn the log filename into an arg option 
"""

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#if os.path.isfile(os.path.abspath("alarm.log")):
#	os.remove(os.path.abspath("alarm.log"))

#handler = logging.FileHandler("alarm.log")
#handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s: [%(funcName)s]: %(message)s')
#handler.setFormatter(formatter)

#stream_handle = logging.StreamHandler()
#stream_handle.setFormatter(formatter)

#logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

def set_log_path(path):
	p = os.path.abspath(path)
	if os.path.isfile(p):
		os.remove(p)

	handler = logging.FileHandler(p)
	handler.setLevel(logging.DEBUG)
	handler.setFormatter(formatter)

	logger.addHandler(handler)