#!/usr/bin/python
import subprocess, sys
from threading import Thread
import os
import signal
import time

class linux_process:
	def __init__(self, cmd, execute=False):
		self.cmd = cmd
		self.output = []
		self.is_running = False
		self.child_pid = None
		if execute:
			self.execute()

	def execute(self):
		if self.is_running == False:
			Thread(target=self._execute_thread).start()
			time.sleep(0.01)
		else:
			print('Process wont execute reason: already running!')
			return -1

	def _execute_thread(self):
		self.is_running = True
		self.p = subprocess.Popen(self.cmd, shell=True, stderr=subprocess.PIPE)
		self.child_pid = self.p.pid
		while True:
		    out = self.p.stderr.readline()
		    if out == '' and self.p.poll() != None:
		        break
		    if out != '':
		    	self.output.append(out)
		    	#print(out)
		self.is_running = False
		self.p = None
		self.child_pid = None

	def get_pid(self):
		return self.child_pid

	def isAvailable_err(self):
		return (len(self.output) > 0)

	def read_next_err(self):
		if self.isAvailable_err():
			ret = self.output[0]
			self.output.pop(0)
			return ret

	def kill_proc(self):
	    if self.child_pid is None:
	        pass
	    else:
	        os.kill(self.child_pid, signal.SIGKILL)
