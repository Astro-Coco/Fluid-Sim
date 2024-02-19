import threading
import subprocess

def run_script(script):
    subprocess.run(["python", script])

thread1 = threading.Thread(target=run_script, args=("sim.py",))
thread2 = threading.Thread(target=run_script, args=("sim.py",))

thread1.start()
thread2.start()

thread1.join()
thread2.join()