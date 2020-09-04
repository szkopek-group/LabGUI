# -*- coding: utf-8 -*-
"""
Created on Wed Apr 05 23:24:14 2017

@author: pfduc
"""
import sys
from types import MethodType
from LocalVars import USE_PYQT5
if USE_PYQT5:
    import PyQt5.QtWidgets as QtGui
    from PyQt5.QtCore import Qt, pyqtSignal
else:
    import PyQt4.QtGui as QtGui
    from PyQt4.QtCore import Qt, SIGNAL
from LabDrivers import SR830 
from numpy import logspace
from math import log10
import time
import numpy as np

class BodeWidget(QtGui.QWidget):
    """This example widget is used to showcase how to create custom widgets."""

    if USE_PYQT5:
        # creates two signals which will be emitted by the widget, we will
        # connect them with the parent of the widget as a listener in the
        # "add_widget_into_main" function (in that case it could also be
        # defined in the "__init__" method.
        # Note: it is important to define the signal at this level of the class
        sg_start_something = pyqtSignal()
        sg_stop_something = pyqtSignal()

    def __init__(self, parent=None, debug=False):
        super(BodeWidget, self).__init__(parent)
        self.DEBUG = debug


        # a button to start something
        self.bt_start = QtGui.QPushButton(self)
        self.bt_start.setText("Start")

        # a button to stop something
        self.bt_stop = QtGui.QPushButton(self)
        self.bt_stop.setText("Stop")

        # assign triggers for the buttons
        if USE_PYQT5:
            self.bt_start.clicked.connect(self.on_bt_start_clicked)
            self.bt_stop.clicked.connect(self.on_bt_stop_clicked)
        else:
            self.connect(
                self.bt_start,
                SIGNAL('clicked()'),
                self.on_bt_start_clicked
            )
            self.connect(
                self.bt_stop,
                SIGNAL('clicked()'),
                self.on_bt_stop_clicked
            )
        
        self.grid = QtGui.QGridLayout()  
        self.FreqLB = 0.01
        self.FreqUB = 100e3
        self.df = 0.001
        self.log_num_samples = 1000
        self.log_current_sample = 0
        self.logspace = []
        temp = logspace(log10(self.FreqLB), log10(self.FreqUB), self.log_num_samples, endpoint=True)
        for point in temp:
            self.logspace.append(round(point,4))
        self.logspace = list(set(self.logspace))
        self.logspace = sorted(self.logspace, key=float)
        self.logspace.reverse()
        #self.logspace.insert(0, self.FreqLB)
        self.log_num_samples = len(self.logspace)
        self.iterations = 1
        self.time_constants = np.asarray([10e-6,30e-6,100e-6,300e-6,1e-3,3e-3,10e-3,30e-3,100e-3,300e-3,1,3,10,30,100,300,1e3,3e3,10e3,30e3])
        self.stopped = True
        self.started = False
        self.paused = False
        self.port="GPIB0::1"
        self.tool=SR830.Instrument(self.port)
        self.logscale = True
        self.set_layout()
        self.resize(480, 600)  
        self.dynamic_time_constant(self.FreqLB)
        self.refresh()

    def find_nearest_tau_enum(self, freq):
        idx = int((np.abs(self.time_constants - 1/freq)).argmin())
        print("tau sec = {} enum = {}".format(self.time_constants[idx], idx))
        return idx

    def on_bt_start_clicked(self):
        """Start something"""
        self.stopped = False
        self.started = True
        self.paused = False
        self.tool.set_ref_internal()
        # self.tool.sync_off()
        self.tool.set_freq(self.logspace[0])
        self.dynamic_time_constant(self.logspace[0])
        # self.run()
        if USE_PYQT5:
            self.sg_start_something.emit()
        else:
            self.emit(SIGNAL("StartSomething()"))

    def on_bt_stop_clicked(self):
        """Stop the server"""
        self.stopped = True
        self.paused = False
        self.started = False
        self.log_current_sample = 0
        if USE_PYQT5:
            self.sg_stop_something.emit()
        else:
            self.emit(SIGNAL("StopSomething()"))




    def set_layout(self):
            """"This method is used to initialise a used defined number of lines of comboboxes, each line will hold information about one instrument"""
            self.vertical_layout = QtGui.QVBoxLayout(self)
            self.vertical_layout.setObjectName("vertical_layout")
            self.vertical_layout.addLayout(self.grid)
            spacer_item = QtGui.QSpacerItem(20, 183, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
            self.vertical_layout.addItem(spacer_item)
            self.setLayout(self.vertical_layout)


            header = QtGui.QLabel("If you just woke me up from the View menu, please keep me open and reboot LabGui \nto enable transient suppressor.\nIf I'm here and you don't need me, please close me and reboot LabGui.")
            self.grid.addWidget(header, 0, 0, 1, 3)

            header = QtGui.QLabel("Set amplitude (V, 0.004 < V < 5.000)")
            self.grid.addWidget(header, 3, 0, 1, 3)
            self.setAmplitudeLe=QtGui.QLineEdit(self)
            self.grid.addWidget(self.setAmplitudeLe, 4,0)
            self.setAmplitudeLe.setFixedWidth(100)
            self.grid.addWidget(self.setAmplitudeLe, 4, 0)

            btn=QtGui.QPushButton(self)
            btn.setObjectName("set_amplitude_button")
            btn.setText('Set Amplitude (V)')
            # self.connect(btn, SIGNAL("clicked()"),self.set_amplitude_handler)
            btn.clicked.connect(self.set_amplitude_handler)
            btn.setFixedWidth(150)
            self.grid.addWidget(btn, 4,2)

            header = QtGui.QLabel("Set frequency lower and upper bounds (Hz, 0.001 < f < 102000)")
            self.grid.addWidget(header, 5, 0, 1, 3)

            self.setFreqLBLe=QtGui.QLineEdit(self)
            self.setFreqLBLe.setObjectName("set_freq_lower_bound")
            self.grid.addWidget(self.setFreqLBLe, 6,0)
            self.setFreqLBLe.setFixedWidth(100)
            self.setFreqUBLe=QtGui.QLineEdit(self)
            self.setFreqUBLe.setObjectName("set_freq_upper_bound")
            self.grid.addWidget(self.setFreqUBLe, 6,1)
            self.setFreqUBLe.setFixedWidth(100)

            btn=QtGui.QPushButton(self)
            btn.setObjectName("set_freq_rng_button")
            btn.setFixedWidth(150)
            btn.setText('Set range (Hz)')
            # self.connect(btn, SIGNAL("clicked()"),self.set_freq_rng_handler)
            btn.clicked.connect(self.set_freq_rng_handler)
            self.grid.addWidget(btn, 6,2)



            self.linlog_header = QtGui.QLabel("Set number of samples per iteration")
            self.grid.addWidget(self.linlog_header , 7, 0, 1, 3)

            self.setdfLe=QtGui.QLineEdit(self)
            self.setdfLe.setObjectName("set_freq_step_size")
            self.grid.addWidget(self.setdfLe, 8,0)
            self.setdfLe.setFixedWidth(100)
            btn=QtGui.QPushButton(self)
            btn.setObjectName("set_freq_step_size_button")
            btn.setFixedWidth(150)
            btn.setText('Set spacing')
            # self.connect(btn, SIGNAL("clicked()"),self.set_freq_step_size_handler)
            btn.clicked.connect(self.set_freq_step_size_handler)
            self.grid.addWidget(btn, 8,2)


            self.iterationheader = QtGui.QLabel("Set number of iterations")
            self.grid.addWidget(self.iterationheader , 9, 0, 1, 3)
            self.setIterationsLe=QtGui.QLineEdit(self)
            self.grid.addWidget(self.setIterationsLe, 10,0)
            self.setIterationsLe.setFixedWidth(100)
            btn=QtGui.QPushButton(self)
            btn.setObjectName("set_iterations_button")
            btn.setFixedWidth(150)
            btn.setText('Set iterations')
            # self.connect(btn, SIGNAL("clicked()"),self.set_iterations_handler)
            btn.clicked.connect(self.set_iterations_handler)
            self.grid.addWidget(btn, 10,2)

            self.cbLogscale = QtGui.QCheckBox("Logscale")
            self.cbLogscale.setChecked(True)
            # self.cbLogscale.stateChanged.connect(self.set_log)
            # self.cbLogscale.stateChanged.connect(self.set_log)
            self.grid.addWidget(self.cbLogscale, 11, 0)



            btn=QtGui.QPushButton(self)
            btn.setObjectName("refresh_button")
            btn.setFixedWidth(150)
            btn.setText('Refresh')
            # self.connect(btn, SIGNAL("clicked()"),self.refresh)
            btn.clicked.connect(self.refresh)
            self.grid.addWidget(btn, 11,2)



            header = QtGui.QLabel("\n\nClick [View - Instrument Setup - Connect] before plotting.\n\nTo flush out current amplifier frequency and start over, use [Clear and Restart].\nTo resume from a pause, please use the [Green Arrow].\n\n")
            self.grid.addWidget(header, 20, 0, 1, 3)

            self.bt_start.setFixedWidth(150)
            self.bt_start.setText('Clear and Restart')
            self.grid.addWidget(self.bt_start, 19,0)

            self.bt_stop.setFixedWidth(150)
            self.grid.addWidget(self.bt_stop, 19,1)

            self.bt_stop.setEnabled(False)
            self.bt_stop.setVisible(False)
            self.bt_start.setVisible(False)



            header = QtGui.QLabel("Select port")
            self.grid.addWidget(header, 30, 0)
            self.cbb = QtGui.QComboBox(self)
            self.cbb.setObjectName("select_port_combo_box")
            self.cbb.setStyleSheet ("QComboBox::drop-down {border-width: 0px;} QComboBox::down-arrow {image: url(noimg); border-width: 0px;}")
            # self.cbb.addItems(self.ports)
            self.cbb.setCurrentIndex(self.cbb.findText("ASRL1::INSTR"))
            self.cbb.setFixedWidth(100)
            # self.connect(self.cbb, SIGNAL("currentIndexChanged(int)"), self.combobox_handler)
            self.cbb.currentIndexChanged.connect(self.combobox_handler)
            self.grid.addWidget(self.cbb, 31, 0)
            btn=QtGui.QPushButton(self)
            btn.setObjectName("set_port_button")
            btn.setFixedWidth(150)
            btn.setText('Set port')
            # self.connect(btn, SIGNAL("clicked()"),self.set_port_handler)
            self.grid.addWidget(btn, 31,2)
            ''''''

    def set_iterations_handler(self):
            self.iterations = int(self.setIterationsLe.text())
            print('Iterations: '+self.setIterationsLe.text())
            self.refresh()

    def set_time_constant_handler(self):
            #tao = self.tool.set_time_constant(self.time_constant_cbb.currentIndex())
            tau = self.dynamic_time_constant(self.FreqLB)
            #print(("Time constant (s) = "+self.time_constants[tau]))
            self.refresh()
            return tau



    def dynamic_time_constant(self, freq):
        pass


    def run (self):
        for freq in self.logspace:
            self.tool.set_freq(freq)
            sleeptime = max(1, 5 / self.tool.get_freq())+2
            print("\nSetter sleeping for tau = {}".format(sleeptime))
            time.sleep(sleeptime)
        self.on_bt_stop_clicked()


    def set_amplitude_handler(self):
            text = self.setAmplitudeLe.text()
            amplitude=0.0
            try:
                amplitude=float(text)
            except:
                print ("Would be nice to have a positive real number.")
                return -1
            amplitude = round(float(text),3)
            if amplitude < 0.004:
                print ("Amplitude (V) beyond permissible range")
                amplitude = 0.004
            if amplitude> 5:
                print ("Amplitude (V) beyond permissible range")
                amplitude = 5
            self.tool.set_amplitude(text+" ")
            newAmp = self.tool.get_amplitude()
            # if abs(newAmp-amplitude)>0.002:
            #     print ("ERROR setting amplitude")
            #     return -1
            self.setAmplitudeLe.setText(str(newAmp))
            print(("Amplitude (V) = "+str(newAmp)))
            self.refresh()
            return newAmp


        # 0.001 <= f <= 102000, resolution 0.0001 Hz
    def set_freq_rng_handler(self):
            textLB = self.setFreqLBLe.text()
            textUB = self.setFreqUBLe.text()
            float1 = 0
            float2 = 0
            try:
                float1=float(textLB)
                float2=float(textUB)
            except:
                print ("Would be nice to have a positive real number.")
                return -1
            if float1 == float2:
                print ("That seems like a point.")
                return -1
            lb = round(min(float1, float2),4)
            ub = round(max(float1, float2),4)
            if lb < 0.001:
                print ("Frequency (Hz) beyond permissible range")
                self.FreqLB = 0.001
            else:
                self.FreqLB = lb

            if ub > 102000:
                print ("Frequency (Hz) beyond permissible range")
                self.FreqUB = 102000
            else:
                self.FreqUB = ub
            print(("Freq Range (Hz): ["+str(self.FreqLB)+", "+str(self.FreqUB)+']'))
            self.refresh()
            return lb, ub

        # df > 0.0001 Hz
    def set_freq_step_size_handler(self):
            text = self.setdfLe.text()
            df=0
            try:
                df=float(text)
            except:
                print ("Would be nice to have a positive real number.")
                return -1
            df = round(df,4)
            if df >= 0.0001:
                self.df = df
            else:
                self.df = 0.0001
                print ("df (Hz) is below hardware resolution")

            self.log_num_samples = int(df)

            if not self.logscale: print(("Linear df (Hz) = "+str(self.df)))
            else: print(("Logscale number of samples = "+str(self.log_num_samples)))

            self.refresh()
            return df


    # GPIB port handling
    def combobox_handler(self):
            return
            port = self.sender().currentText()
            self.port=port;
            self.emit(SIGNAL("set_port_SRS830(QString)"),port)

    def set_instrument(self,instrument):
            print(instrument)
            field = instrument.measure("FREQ")
            if field is None:
                print("error setting instument")
            else:
                self.tool = instrument
                self.read_mode_handler()
                self.read_set_point()
                self.read_rate()

    def dynamic_time_constant(self, lb):
        pass

    def refresh(self):
            self.setAmplitudeLe.setText(str(self.tool.get_amplitude()))
            #self.time_constant_cbb.setCurrentIndex(self.tool.get_time_constant())
            self.setFreqLBLe.setText(str(self.FreqLB))
            self.setFreqUBLe.setText(str(self.FreqUB))
            self.setIterationsLe.setText(str(self.iterations))
            if self.logscale:
                self.setdfLe.setText(str(self.log_num_samples))
                self.logspace = []
                single_iteration_logspace = []
                temp = logspace(log10(self.FreqLB), log10(self.FreqUB), self.log_num_samples, endpoint=True)
                for point in temp:
                    single_iteration_logspace.append(round(point,4))
                single_iteration_logspace = list(set(single_iteration_logspace))
                single_iteration_logspace = sorted(single_iteration_logspace, key=float)
                for i in range(0,self.iterations):
                    single_iteration_logspace=single_iteration_logspace[::-1]
                    self.logspace.extend(single_iteration_logspace)
                print(self.logspace)
                self.log_current_sample = 0
            else:
                self.dynamic_time_constant(self.FreqLB)
                self.setdfLe.setText(str(self.df))



def do_something_function(parent):
    """Definition of a method which will be assigned to LabGuiMain instance
    and connected to the sg_start_something signal"""
    # make sure the debug mode is set to True
    if not parent.DEBUG:
        parent.option_change_debug_state()

    # connect the instrument hub
    parent.connect_instrument_hub()
    # start the datataker
    parent.start_DTT()


def stop_things_function(parent):
    """Definition of a method which will be assigned to LabGuiMain instance
    and connected to sg_stop_something signal"""

    # stop the datataker
    parent.stop_DTT()


def add_widget_into_main(parent):
    """add a widget into the main window of LabGuiMain through this function
    create a QDock widget and store a reference to the widget in a dictionary
    """

    mywidget = BodeWidget(parent=parent)
    widget_name = "BodeWidget"

    # fill the dictionary with the ExampleWidget instance added into LabGuiMain
    parent.widgets[widget_name] = mywidget

    # create a QDockWidget
    dock_widget = QtGui.QDockWidget("Bode", parent)
    dock_widget.setObjectName("bodeWidgetDockWidget")
    dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    dock_widget.setWidget(mywidget)
    parent.addDockWidget(Qt.LeftDockWidgetArea, dock_widget)

    # Enable the toggle view action of this widget as a "window" menu option
    parent.windowMenu.addAction(dock_widget.toggleViewAction())
    dock_widget.show()

    # assigning the method defined in this file to the parent class so we can
    # use them to setup signals between our ExampleWidget and LabGuiMain
    if sys.version_info[0] > 2:
        # python3
        parent.do_something = MethodType(do_something_function, parent)
        parent.stop_things = MethodType(stop_things_function, parent)

    else:
        # python2
        parent.do_something = MethodType(do_something_function, parent,
                                         parent.__class__)
        parent.stop_things = MethodType(stop_things_function, parent,
                                        parent.__class__)

    # now we connect these newly assigned methods of LabGuiMain to the signal
    # of our ExampleWidget (each added widgets will be in the self.widget
    # dictionary of LabGuiMain with key entry corresponding to the widget name
    # in this case it is "ExampleWidget"
    if USE_PYQT5:
        # Whenever the signal is triggered by ExampleWidget, the method
        # "do_something" of "LabGuiMain" will be called
        parent.widgets[widget_name].sg_start_something.connect(
            parent.do_something)

        # Whenever the signal is triggered by ExampleWidget, the method
        # "stop_things" of "LabGuiMain" will be called
        parent.widgets[widget_name].sg_stop_something.connect(
            parent.stop_things)
    else:
        parent.connect(parent.widgets[widget_name], SIGNAL(
            "StartSomething()"), parent.do_something)

        parent.connect(parent.widgets['InstrumentWidget'], SIGNAL(
            "StopSomething()"), parent.stop_thing)


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    ex = BodeWidget()
    ex.show()
    sys.exit(app.exec_())
