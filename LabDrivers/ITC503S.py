import time
import random
import visa

try:
    from . import Tool
except:
    import Tool

#param = {'T1': 'K', 'T2': 'K', 'T3': 'K'}

param = {
    'T_SET' : 'K',
    'T1' : 'K',
    'T2' : 'K',
    'T3' : 'K',
    'T_ERR' : 'K',
    'HEATER_OP': '%',
    'HEATER_OP': 'V',
    'GAS_FLOW' : 'arbitrary'
    """
    Others include (in this order)
    Proportional Band
    Integral Action Time
    Derivative Action Time
    Channel 1 Freq
    Channel 2 Freq
    Channel 3 Freq
    """

}

INTERFACE = Tool.INTF_GPIB


# READ THE MANUAL for RS232 interfacing page 9 chapter 3.3 have to find a 25 to 9 pin connector, we only care about pins 1-3

class Instrument(Tool.MeasInstr):

    def __init__(self, resource_name, debug=False,**kwargs):
        print(kwargs)
        if "interface" in kwargs:
            itfc = kwargs.pop("interface")
        else:
            itfc = INTERFACE

        name='ITC503S'
        if "name" in kwargs:
            name = kwargs.pop("name")
            print(name)
        # there is an error regarding the query: *IDN? posed at the beginning.
        # this error leaves the error message ?*IDN? in the
        is_empty = True
        super(Instrument, self).__init__(resource_name, name=name, debug=debug, interface = itfc, read_termination = '\r', **kwargs)

        #self.term_chars = '\r'

        #self.term_chars = '\r'
        #self.connection.read_termination = '\r'
        self.setControl(False, True) #still works with 0,1; but improper
        """ FOR FIRST INSTANCE ONLY
        try:
            self.connection.read()
        except:
            pass #really bad programming technique ik
        """
        #self.write('$W1000')
        #print("working") will not get to this point
    """
    def measure_old(self, channel): #consider rewriting
        if channel in self.last_measure:
            if channel == 'T1':
                if not self.DEBUG:
                    self.write('R1')
                    is_empty = True
                    idx = 0
                    while is_empty:
#                        print(idx)
                        idx = idx + 1
                        answer = self.read()
#                        print(answer)
                        if answer:
                            is_empty = False
                    answer = float(answer.split('R')[1])
                    #self.read() # weird empty string after each reading - this is to get rid of that
                else:
                    answer = random.random()
                self.last_measure[channel] = answer

            elif channel == 'T2':
                if not self.DEBUG:
                    self.write('R2')
                    is_empty = True
                    answer = ''
                    while is_empty:
                        temp_answer = self.read()
                        answer= answer + temp_answer
#                        print(answer)
                        if temp_answer:
                            is_empty = False
                    answer = float(answer.split('R')[1])
                    #self.read() # weird empty string after each reading - this is to get rid of that
                else:
                    answer = random.random()
                self.last_measure[channel] = answer

            elif channel == 'T3':
                if not self.DEBUG:
                    # 0 #this is to be defined for record sweep
                    self.write('R3')
                    #self.write('$W1000')
                    answer = ''
                    idx = 0
                    is_empty = True
                    while is_empty:
                        idx = idx + 1
                        #print(idx)
                        temp_answer = self.read()
                        answer= answer + temp_answer
#                        print(answer)
                        if temp_answer:
                            is_empty = False
                    answer = answer.split('R')
#                    print("%s" % answer)
                    answer = float(answer[1])
                    #self.read() # weird empty string after each reading - this is to get rid of that
                else:
                    answer = random.random()
                self.last_measure[channel] = answer

        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None
        return answer
        
           # set controls for locked (0 = False, 1 = True) and remote (0 = local, 1 = remote)
    """
    def measure(self, channel):
        if channel in self.last_measure:
            command = "R" + str(list(param.keys()).index(channel))
            answer = self.query(command)
            self.last_measure[channel] = answer
        else:
            print("you are trying to measure a non existent channel : " + channel)
            print("existing channels :", self.channels)
            answer = None


        return float(answer.split("R")[-1]) # last data point incase it reads two
    """
    def setControl_old(self, locked, remote):
        if locked and remote:
            self.write('$C1')
        elif locked:
            self.write('$C0')
        elif remote:
            self.write('$C3')
        else:
            self.write('$C2')
    """
    def setControl(self, locked, remote):
        # same principles, its a binary number whos first bit is 0:local, 1:remote, and second bit is 0:lock, 1:unlock
        unlocked = not locked
        commandcode = int( str(int(unlocked)) + str(int(remote)), 2)
        self.write('$C'+str(commandcode))

    def setHeaterAndGas(self, heater_auto, gas_auto):
        # these values MUST be booleans! TODO: implement check
        commandcode = int( str(int(gas_auto)) + str(int(heater_auto)), 2)
        # the way it works is An, where n is a decimal number, whos first bit (2^0) represents if heater is auto, and second bit represents if gas flow is auto
        self.write("$A"+str(commandcode))

    def setSweep(self, line, PointTemperature, SweepTime, HoldTime):
        line = int(line)
        if (line >= 1) and (line <= 16):
            self.write("$x"+str(line))
            #if x not in 'x':
            #    print("Error writing x:" + x)

            values = [PointTemperature, SweepTime, HoldTime]
            i=1
            for x in values:
                # point temperature
                self.write("y"+str(i))
                y = self.read()
                if y not in 'y':
                    print("Error writing y:" + y)
                # write value
                self.write("s" + str(x))
                s = self.read()
                if s not in 's':
                    print("Error writing s:" + s)
                i += 1
        else:
            print("Invalide line")

    def readSweep(self, line):
        line = int(line)
        if (line >= 1) and (line <= 16):
            self.write("x"+str(line))
            err = self.read()
            if 'x' != err[:1]:
                print("Error writing x: "+err)

            values_r = ["Point Temperature", "Sweep Time", "Hold Time"]
            values_w = [None] * 3
            for i in range(3):
                self.write("y"+str(i+1))
                err = self.read()
                if 'y' != err[:1]:
                    print("Error writing y: " + err)

                self.write("r")
                ret = self.read()
                if '?' == ret[:1]: #command error'd
                    print("Error reading value: " + ret)
                else:
                    values_w[i] = ret[1:]
            for values in list(zip(values_r, values_w)):
                print(values[0]+": "+values[1])
            return [float(i) for i in values_w]
            """ try: Possible catch for return variable just in case
                return [float(i) for i in values_w]
            except ValueError:
                # need to do it manually cuz smn is fucked up
                ret_arr = []
                j=0
                for i in values_w:
                    try:
                        ret_arr.append(float(i))
                    except:
                        ret_arr.append(None)
                        pass
                return ret_arr"""
        else:
            print("Invalid sweep line")
            return [None]*3

    def wipeSweep(self):
        self.write("w")
        ret = self.read()
        if '?' == ret[:1]:
            print("ITC is either in local or currently running a sweep")
        else:
            print("Sweep values wiped")



    def query(self, command):
        self.write(command)
        is_empty = True
        idx = 0
        answer = ''
        while is_empty:
            #                        print(idx)
            idx = idx + 1
            answer = self.read()
            #print(answer)
            if answer and answer is not "?*IDN?": #bug fix for when first connected, ?*IDN? is still in read buffer
                is_empty = False
        return answer

if (__name__ == '__main__'):
    i = Instrument("GPIB0::24")
    i.setControl(False, True)

    i.setSweep(1,100,10,1)
    i.readSweep(1)
    i.wipeSweep()
    i.readSweep(1)
    while True: #yuck
        cmd = input("Enter command: ")
        print(i.query(cmd))
    i.close()


#   print(i.write('R1'))
#   is_empty = True
#   idx = 0
#   while is_empty:
#       idx = idx+1

#       answer = i.read()
#       print("%i:'%s'"%(idx, answer))
#       if answer:
#           is_empty = False
#  print(answer)
            
#    print(i.measure('T1'))
#    print(i.measure('T3'))
#    print(i.measure('T2'))
#    print(i.measure('T3'))
#    print(i.measure('T1'))
##    print(i.measure('T3'))
#    print(i.measure('T2'))
#    print(i.measure('T1'))
#    print(i.measure('T3'))
#    print(i.measure('T1'))
#    print(i.measure('T3'))
#   print(i.measure('T2'))
#    print(i.measure('T1'))






#    term_char = '\r' 
#    rm = visa.ResourceManager()
#    i = rm.get_instrument("GPIB0::24")
#    i.write("$C3" + term_char)
#    i.write('R3' + term_char)
#    i.read()
#    i.close()
    #print(i.ask('V\r'))
    #i.write('$R2\r')
    #a = i.read()
    #print(a)