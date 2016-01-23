import time
import roboclaw
from diagnostics import display_errors
from dbgp.client import brk

ADDRESS = 0x80

########################################################

def forwardRight(value):
    print "Forward Right %d %d" % (value, roboclaw.ForwardM1(ADDRESS, value))    

def forwardLeft(value):
    print "Forward Left %d %d" % (value, roboclaw.ForwardM2(ADDRESS, value))
    
########################################################

def stop():
    forwardLeft(0)
    forwardRight(0)

########################################################

def main(): 
    roboclaw.Open("/dev/ttyAMA0",115200)
    
    print "Set minimum voltage for main battery %d" % roboclaw.SetMinVoltageMainBattery(ADDRESS, 0)    
    
    stop()
    
    for x in range(0, 127):        
        forwardLeft (x)
        forwardRight(x)
        display_errors (roboclaw.ReadError(ADDRESS))
        time.sleep(1)        

    stop()
    
if __name__ == "__main__":
    try: 
        main()
    finally:
        stop()
