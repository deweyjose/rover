import sys
import RPi.GPIO as GPIO
import time
import loggers
from settings import rconn

LOGGER         = loggers.get_logger(__file__, loggers.get_info_level())
TRIGGER_PIN    = 23
ECHO_PIN       = 24
SPEED_SOUND_CM = 17150

########################################################

def startup(settle_time=2):
    LOGGER.info("startup")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIGGER_PIN,GPIO.OUT)
    GPIO.setup(ECHO_PIN,GPIO.IN)
    GPIO.output(TRIGGER_PIN, False)
    LOGGER.info("Wait for sensor to settle after {0} seconds".format(settle_time))
    time.sleep(settle_time)

########################################################

def shutdown():
    LOGGER.info("shutdown")
    GPIO.cleanup()

########################################################

def read_distance(speed=SPEED_SOUND_CM):
    LOGGER.debug("read_distance")
    
    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, False)

    pulse_start = time.time()
    while GPIO.input(ECHO_PIN)==0: pulse_start = time.time()
    
    pulse_end   = time.time()
    while GPIO.input(ECHO_PIN)==1: pulse_end   = time.time()
    
    duration = pulse_end - pulse_start
    distance = duration * speed
    distance = round(distance, 2)
    
    LOGGER.debug("Distance: {0}cm".format(distance))
    
    return distance

if __name__ == '__main__':
    delay = float(sys.argv[1])
    limit = float(sys.argv[2])
    
    startup()
    
    while True:
        current_distance = read_distance()
        if current_distance < limit:
            LOGGER.warn("stopping rover. current distance is {0}cm".format(current_distance))
            rconn.publish('rover', 'stop')
        time.sleep(delay)