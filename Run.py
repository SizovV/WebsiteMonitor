import subprocess

while True:
    process = subprocess.Popen(['python3',"main.py"])
    process.wait()