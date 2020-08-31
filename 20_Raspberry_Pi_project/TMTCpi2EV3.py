#!/usr/bin/python3
############################################################
# Class TMTCpi2EV3
# This class realizes the communication between
# the pi and the EV3 using telemetry and telecommands
# With TCs the EV3 is commanded and it answers TMs.
# This class also defines the communication
# behaviour depending on the TC.
#
# This class is only used on Raspberry Pi not on Windows PC

# File: TMTCpi2EV3.py
# Author: Detlef Heinze 
# Version: 1.4    Date: 22.07.2020      
###########################################################

import EV3mailbox   #De- and encoding of EV3 mailbox messages
import time
import platform as pf

if pf.system() == 'Linux':
    import serial

class TMTCpi2EV3(object):
    
    # Constructor: Open serial port to EV3
    def __init__(self, serialPort, mailboxName):
        self.serialPort = serialPort
        self.EV3serial = serial.Serial(serialPort)
        self.mailboxName = mailboxName
        print('Device: ' + self.serialPort + ' using mailbox: ' + mailboxName)
    
    
    #Send a telecommand to the EV3. This textual message must be acknowledged by the EV3
    #within 2 seconds. An additional answer (Telemetry) may be requested by Pi
    #and send by EV3 within a timeout "withinSeconds".
    #Input parameter :
    #    aCommandString: a string containing a command for the EV3.
    #    TMexpected:     aBoolean which denotes if a TM should be send by EV3
    #    withinSeconds:  Timeout for the replied TM from EV3
    #Output parameter:
    #    a Boolean if the whole TC has executed well.
    #    aString containing the optional TM
    def sendTC(self, aCommandString, TMexpected, withinSeconds=1):
        #Encode telecommand
        s = EV3mailbox.encodeMessage(EV3mailbox.MessageType.Text, self.mailboxName, aCommandString)
        print('\nSending the following message: ' + aCommandString)
        print(EV3mailbox.printMessage(s))
        
        #Write message to the bluetooth port and send the command.
        self.EV3serial.write(s)
        #Has the TC been received by EV3?
        wait=True
        ackCommand=False
        ackTM= False
        timeout = time.time() + 2  # Within 2 seconds expect acknowlegdement by EV3
        while wait and time.time() < timeout: 
            n = self.EV3serial.in_waiting
            if n != 0:
                s = self.EV3serial.read(n)
                mail,value,s = EV3mailbox.decodeMessage(s, EV3mailbox.MessageType.Logic)
                if value:
                    print('TC sent and acknowledged')
                else:
                    print('TC sent and NOT acknowledged')
                ackCommand=value
                wait = False
            else:
                # Waiting for data to arrive
                time.sleep(0.1)
        
        #Do we expect a reply by TM?
        if ackCommand and TMexpected:
            wait=True
            value= None
            # Expect execution of command "withinSeconds"
            timeout = time.time() + withinSeconds
            while wait and time.time() < timeout:
                n = self.EV3serial.in_waiting
                if n != 0:
                    s = self.EV3serial.read(n)
                    mail,value,s = EV3mailbox.decodeMessage(s, EV3mailbox.MessageType.Text)
                    print('TM received: ' + value)
                    ackTM=True
                    wait = False
                else:
                    # Waiting for data to arrive; cool down processor
                    time.sleep(0.1)
            return (ackCommand and ackTM, value)
        else:
            if not TMexpected:
                print("No TM expected")
            return (ackCommand, "")
          

        
    
    
    