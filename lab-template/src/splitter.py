import subprocess
import time

# run src/algorithms/mining/main.py and then wait 5 seconds to run src/algorithms/mining/client/main.py

# Run src/algorithms/mining/main.py
subprocess.run(['python', 'src/algorithms/mining/main.py'])

# Wait for 5 seconds
time.sleep(5)

# Run src/algorithms/mining/client/main.py
subprocess.run(['python', 'src/algorithms/mining/client/main.py'])