
import os
import argparse

from alarm import AlarmPool, Alarm, get_date, logger

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("--debug", action="store_true")
	args = parser.parse_args()

	try:
		pool = AlarmPool("alarm.config")
		
		logger.info("script starting up @ %s" % str(get_date()))
		Alarm.set_volume(90) # should be between 100 and 85
		
		pool.load()

		if args.debug:
			logger.info("*** running debug mode... ***")
			pool.debug()
		else:
			pool.run()

	except KeyboardInterrupt:
		logger.exception("keyboard interrupt")

	except:
		logger.exception("exception occured")
		raise

	logger.info("script finishing up @ %s" % str(get_date()))

if __name__ == "__main__":
        main()
