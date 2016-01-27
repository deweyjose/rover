import sys
import time
import loggers
import motorctrl
import diagnostics
import commands
from settings import rconn

LOGGER = loggers.get_logger(__file__, loggers.get_default_level())
        
if __name__ == '__main__':
    try:
        motorctrl.startup()
        
        version = motorctrl.get_version()
        
        if version.ok == False:
            LOGGER.error("Failed to get version from motor controller")
            
        LOGGER.info("Let's start Driving with \"{0}\"".format(version.version))
            
        motorctrl.set_voltage_settings(motorctrl.voltage_settings(0))
        motorctrl.stop()
        
        LOGGER.info('starting queue processing mode')    
    
        pubsub = rconn.pubsub()
        pubsub.subscribe('rover')

        while True:
            for item in pubsub.listen():
                message = item['data']
                if message == int(1):
                    continue
                if commands.execute(message) == False:
                    break        
    finally:
        motorctrl.stop()

