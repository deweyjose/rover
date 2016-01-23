import time
import roboclaw
from diagnostics import display_errors
from dbgp.client import brk

ADDRESS = 0x80

########################################################

def backward_right(value):
    print "Backward Right %d %d" % (value, roboclaw.BackwardM1(ADDRESS, value))

def backward_left(value):
    print "Backward Left %d %d" % (value, roboclaw.BackwardM2(ADDRESS, value))    

def forward_right(value):
    print "Forward Right %d %d" % (value, roboclaw.ForwardM1(ADDRESS, value))    

def forward_left(value):
    print "Forward Left %d %d" % (value, roboclaw.ForwardM2(ADDRESS, value))

def forward(value):
    forward_right(value)
    forward_left(value)

def backward(value):
    backward_right(value)
    backward_left(value)
    
def turn_left(value):
    forward_left(40)
    forward_right(10)

def turn_right(value):
    forward_left(10)
    forward_right(40)

def spin(value):
    forward_left(25)
    backward_right(25)

def stop():
    forward_right(0)
    forward_left(0)

########################################################

def main(): 
    roboclaw.Open("/dev/ttyAMA0",115200)
    
    print "Set minimum voltage for main battery %d" % roboclaw.SetMinVoltageMainBattery(ADDRESS, 0)    
    
    stop()
    spin(1)
    time.sleep(10)

    for x in range(0, 2):    
        forward(40)
        time.sleep(5)
        
        stop()
        time.sleep(5)
        
        backward(40)
        time.sleep(5)
        
        stop()
        time.sleep(5)
        
        backward(40)
        time.sleep(5)
        
        turn_left(20)
        time.sleep(5)
        
        turn_right(20)
        time.sleep(5)
        
        forward(40)
        time.sleep(5)
        
        spin(25)
        time.sleep()
    
    stop()
    
if __name__ == "__main__":
    try: 
        main()
    finally:
        stop()
