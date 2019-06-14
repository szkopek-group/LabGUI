# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 2019

@author: zackorenberg

A module designed to allow user scripts (for sweeps for example) to run with start/stop/pause concurrently with normal script and plot live data in separate graph.
"""

# -*- coding: utf-8 -*-
"""
Created for GervaisLabs
"""
# for testing
try:
    USE_PYQT5
except:
    USE_PYQT5 = True


if USE_PYQT5:

    import PyQt5.QtWidgets as QtGui
    from PyQt5.QtCore import Qt, pyqtSignal, QRect, QRectF, QThread, QMutex

else:

    import PyQt4.QtGui as QtGui
    from PyQt4.QtCore import Qt, QRect, QRectF
    from PyQt4.QtCore import SIGNAL

from importlib import import_module
import importlib.util

def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

import LabTools.IO.IOTool as IOTools

import inspect
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

FORBIDDEN_SCRIPTS = ['userscript_example.py', '__init__.py','UserTool.py']

class UDataTaker(QThread):

    if USE_PYQT5:
        data = pyqtSignal('PyQt_PyObject')

        script_finished = pyqtSignal(bool)

    def __init__(self, lock, instr_hub, parent=None, debug=False):
        super(UDataTaker, self).__init__(parent)
        self.lock = lock
        self.instr_hub = instr_hub

        self.DEBUG = debug



        self.parent = parent
        self.scripts = {}
        self.active_scripts = {}

        self.mutex = QMutex()

        self.running = False
        self.stopped = True
        self.paused = False
        self.completed = False  # only true when all scripts finish

        self.script_folder = IOTools.get_userscript_directory()
        print(self.script_folder)
        self.load_scripts()

        if USE_PYQT5:

            self.instr_hub.changed_list.connect(self.reset_devices)

        else:

            self.connect(self.instr_hub, SIGNAL(
                "changed_list()"), self.reset_devices)
        self.reset_devices()




    def load_scripts(self):
        # called at the beginning of the function, imports all scripts and creates object for them
        user_scripts = os.listdir(self.script_folder)
        sys.path.append(self.script_folder)
        print(user_scripts)
        for file in user_scripts:
            if file.endswith(".py") and file not in FORBIDDEN_SCRIPTS:
                print(file)

                name = file.split('.py')[0]
                module = module_from_file(name, os.path.join(self.script_folder, file))
                self.scripts[name] = module
                self.active_scripts[name] = False # so it exists
                print("Testing devices:", 'KT2500' in module.devices)
                Test = module.Script()
                Test.announce()



    def reset_devices(self):
        if self.instr_hub:
            self.instrument_list = self.instr_hub.get_instrument_list()
            z = self.instrument_list.items()

            ports = list()
            instruments = list()
            names = list()
            for x, y in z:
                if x is not None and "ComputerTime" not in x:
                    ports.append(x)
                    instruments.append(self.instrument_list[x])
                    names.append(self.instrument_list[x].ID_name)
                    # print(x,self.instrument_list[x].ID_name)
            self.sanitized_list = list(zip(names, ports, instruments))
            self.instruments = {}
            for name, instrument in zip(names, instruments):
                self.instruments[name] = instrument


        elif self.DEBUG: # TODO SET DEBUG PARAMS
            self.instrument_list = {}
            self.sanitized_list = []
            self.instruments = {}

        print(self.instruments)
        print(self.sanitized_list)

    def set_script_active(self, script, active:bool):
        if script in self.active_scripts.keys():
            self.active_scripts[script] = active
    def get_script_active(self, script):
        if script in self.active_scripts.keys():
            return self.active_scripts[script]
    def toggle_script_active(self, script):
        if script in self.active_scripts.keys():
            self.active_scripts[script] = not self.active_scripts[script]
            return self.active_scripts[script]

    def create_script(self, path, device=[], properties={}):
        print(path)




    def clear_scripts(self):
        # TODO: check if run lock
        self.scripts.clear()
        #for script in self.scripts:


    ### RUNNING OPERATORS ###
    def initialize(self):
        # might be useful later
        print("initialize working")
    ### when .start() is called ###

    def run(self):
        print("Reached here")



    ### Copied almost vertabim from DataManagement.py ###

    def isRunning(self):

        return self.running

    def isPaused(self):

        return self.paused

    def isStopped(self):

        return self.stopped

    def ask_to_stop(self):

        self.stopped = True
        self.paused = False

    def resume(self):
        print("reached resume")




## class which each Script object inherits ##
class UserScript(QThread):
    """
    Important inheritable functions are:
    appendData(*args), where args must be same length as # channels

    Uses QThread so can be launched with inherited .start()
    """
    def __init__(self, instr_hub = None, parent=None, debug=False):
        super(UserScript, self).__init__(parent)

        self.instr_hub = instr_hub
        self.DEBUG = debug
        self.parent = parent

        self.params = {}
        self.properties = {}
        self.devices = {}
    def set_property(self, name, value):
        setattr(self, name, value)
    def get_property(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return None

    def addData(self, *args): # DO NOT OVERRIDE
        
