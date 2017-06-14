#!/usr/bin/env python
import random
import numpy as np
import logging

try:
    from . import Tool
except:
    import Tool

CHANNELS_IDX = {"1K Pot":"LS_1","Still":"LS_2","ICP":"LS_3","MC":"LS_4"}

param = {'heater': '%',"1K Pot":"K","Still":"K","ICP":"K","MC":"K"}

INTERFACE = Tool.INTF_GPIB

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug = False, **kwargs):
        super(Instrument, self).__init__(resource_name, 'LS370_janis', debug=debug,
                                         interface = INTERFACE, timeout=12, **kwargs)

    def measure(self, channel):
        if channel in self.last_measure:
            if not self.DEBUG:
                if channel == 'heater':
                    return self.get_heater_output()
                else:
                    answer = self.read_channel(CHANNELS_IDX[channel])

            else:
                answer = random.random()
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer

    def read_channel(self, chan):
        if not self.DEBUG:
            data = self.ask('RDGR? ' + str(chan[-1]))

            try:
                return float(data)
            except:
                logging.error("the reading from the lakeshore 370 is no a number, please check that the timout is sufficiently large, 0.1 s is too short")

                        
        else:
            return 1337.0

    def set_heater_range(self, htr_range):
        if not self.DEBUG:
            if htr_range >= 0 and htr_range < 9:
                self.write('HTRRNG %d' % htr_range)

    def get_heater_range(self):
        if not self.DEBUG:
            return float(self.ask('HTRRNG ?'))
        else:
            return 0

    def set_heater_output(self, percent):
        if not self.DEBUG:
            if percent >= 0 and percent <= 100:
                self.write('MOUT %.3f' % percent)

    def get_heater_output(self):
        if not self.DEBUG:
            return float(self.ask('MOUT ?'))
        else:
            return 0

    def auto_scan(self):
        if not self.DEBUG:
            self.write('SCAN 1,1')

    def scanner_to_channel(self, chan):
        if not self.DEBUG:
            self.write('SCAN %d,0' % chan)


if (__name__ == '__main__'):


    i = Instrument("GPIB0::12")
    print(i.identify())
    print(i.measure("1K Pot"))
    print(i.measure("ICP"))
    
