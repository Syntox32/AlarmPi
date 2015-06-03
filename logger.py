import os
import logging

# setup all the logger stuff
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if os.path.isfile(os.path.abspath("alarm.log")):
	os.remove(os.path.abspath("alarm.log"))

handler = logging.FileHandler("alarm.log")
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s: [%(funcName)s]: %(message)s')
handler.setFormatter(formatter)

#stream_handle = logging.StreamHandler()
#stream_handle.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())
