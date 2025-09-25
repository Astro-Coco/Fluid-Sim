import threading
import subprocess

def run_script(script):
    subprocess.run(["python", script])

thread1 = threading.Thread(target=run_script, args=("sim.py",))
thread2 = threading.Thread(target=run_script, args=("sim.py",))
thread3 = threading.Thread(target=run_script, args=("sim.py",))
thread4 = threading.Thread(target=run_script, args=("sim.py",))

thread1.start()
thread2.start()
thread3.start()
thread4.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()