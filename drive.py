import time
import loggers
import motorctrl
import diagnostics

LOGGER   = loggers.get_logger(__file__, loggers.get_debug_level())

#            COMMAND     FUNCTION         
commands = {'forward'    : motorctrl.forward,
            'f'          : motorctrl.forward,
            'backward'   : motorctrl.reverse,
            'b'          : motorctrl.reverse,
            'left'       : motorctrl.turn_left,
            'l'          : motorctrl.turn_left,
            'right'      : motorctrl.turn_right,
            'r'          : motorctrl.turn_right,
            'spin'       : motorctrl.spin,
            's'          : motorctrl.spin,    
            'stop'       : motorctrl.stop,
            'x'          : motorctrl.stop,
            'accelerate' : motorctrl.accelerate,
            'a'          : motorctrl.accelerate,
            'decelerate' : motorctrl.decelerate,
            'd'          : motorctrl.decelerate,
            'diagnostics': diagnostics.print_info_dictionary,
            'z'          : diagnostics.print_info_dictionary,
            'help'       : None,
            'h'          : None,
            'quit'       : None,
            'q'          : None}
#           COMMAND      FUNCTION         
        
########################################################

def main():
    motorctrl.startup()
    
    version = motorctrl.get_version()
    
    if version.ok == False:
        LOGGER.error("Failed to get version from motor controller")
        
    LOGGER.info("Let's start Driving with \"{0}\"".format(version.version))
        
    motorctrl.set_voltage_settings(motorctrl.voltage_settings(0))
    motorctrl.stop()    
    
    while True:
        cmd = raw_input('Enter a command: ')
        
        if cmd == 'help' or cmd == 'h':
            LOGGER.info("FUNCTIONS: %s" % ' '.join(commands.keys()))
            continue
        elif cmd == 'quit' or cmd == 'q':
            LOGGER.info("good bye!")
            break        
        else:        
            func_info = commands.get(cmd)
        
            if func_info == None:
                LOGGER.error("Unknown command %s" % cmd)
                continue
            else:            
                func = func_info
                if func != None:
                    func()                    

try: 
    main()
finally:
    motorctrl.stop()
