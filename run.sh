
# kills previous jobs if they are lingering around
pkill -f "python alarm.py"

# run in the background so we can exit the sessions
# without disrupting the process
nohup python alarm.py --config alarm.config &

# any 'direct' console output can be read by typing 
# 'cat nohup.out' in the same directory