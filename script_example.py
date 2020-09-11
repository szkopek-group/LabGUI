# -*- coding: utf-8 -*-
"""
Created on Tue May 21 21:38:20 2013

@author: Ben

This is a script to be used with DataTaker.py, part of the LabGui.py
program. This example just loops until the thread is killed. It runs within 
the namespace of DataTaker.
"""

print("INIT DONE")
self.widget.log_current_sample = 0
# print self.instruments
while self.isStopped() == False and self.widget.log_current_sample<len(self.widget.logspace):
    freq = self.widget.logspace[self.widget.log_current_sample]
    tau_enum = self.widget.tool.set_tau( self.widget.find_nearest_tau_enum(float(freq)))

    print("Set freq to {} Hz".format(freq))
    self.widget.tool.set_freq(freq)

    tau_sec = self.widget.time_constants[tau_enum]
    multiplier = 5
    minWaitTimeInSec = 5
    sleeptime = max(minWaitTimeInSec, multiplier * tau_sec)
    print("Sleeping for {} sec at freq = {}\n".format(sleeptime, self.widget.logspace[self.widget.log_current_sample]))
    time.sleep(sleeptime)

    self.read_data()
    self.check_stopped_or_paused()
    self.widget.log_current_sample += 1
