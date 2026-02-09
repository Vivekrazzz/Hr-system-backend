import subprocess
import time
import os

# Start server
server = subprocess.Popen(['python', 'manage.py', 'runserver', '8005'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         text=True)

time.sleep(10)

# Run test
try:
    # Update test script to use 8005
    with open('test_workflow_8005.py', 'w') as f:
        f.write(open('test_workflow_8001.py').read().replace('8001', '8005'))
    
    test_out = subprocess.check_output(['python', 'test_workflow_8005.py'], text=True, stderr=subprocess.STDOUT)
    print("Test Output:")
    print(test_out)
except subprocess.CalledProcessError as e:
    print("Test Failed Output:")
    print(e.output)

# Stop server
server.terminate()
stdout, stderr = server.communicate()
print("\nServer Stdout:")
print(stdout)
print("\nServer Stderr:")
print(stderr)
