
from alarm import AlarmPool, Alarm, get_date, logger

def main():
	"""
	Main or something
	"""

	logger.info("script starting up @ %s" % str(get_date()))

	try:
		Alarm.set_volume(90) # should be between 100 and 85

		#q = "Good morning Syntox!. Today's weather is quite nice. This sentence is about to be over a hundred characters long and this is not good for the tts thing because it will truncate it" 
		#q = "Good morning Henning!. What the fuck are you talking about? Why is this not working"
		#q = "Good morning Syntox!. Todays weather is quite nice" 

		#q1 = "This is one query This is one query This is one query This is one query This is one query This is one query"
		#q2 = "This is a second query"
		#q3 = "This is a third query"

		pool = AlarmPool()
		pool.load()
		pool.debug()
		#pool.run()

	except KeyboardInterrupt:
		logger.exception("keyboard interrupt")

	except:
		logger.exception("exception occured")
		raise

	logger.info("script finishing up @ %s" % str(get_date()))

if __name__ == "__main__":
        main()