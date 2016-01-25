import RPi.GPIO as GPIO
import time
import loggers

LOGGER         = loggers.get_logger(__file__, loggers.get_debug_level())
TRIGGER_PIN    = 23
ECHO_PIN       = 24
SPEED_SOUND_CM = 17150

########################################################

def startup(settle_time=2):
    LOGGER.debug("startup")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIGGER_PIN,GPIO.OUT)
    GPIO.setup(ECHO_PIN,GPIO.IN)
    GPIO.output(TRIGGER_PIN, False)
    LOGGER.debug("Wait for sensor to settle after {0} seconds".format(settle_time))
    time.sleep(settle_time)

########################################################

def shutdown():
    LOGGER.debug("shutdown")
    GPIO.cleanup()

########################################################

def read_distance(speed):
    LOGGER.debug("read_distance")
    
    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, False)

    while GPIO.input(ECHO_PIN)==0: pulse_start = time.time()      
    while GPIO.input(ECHO_PIN)==1: pulse_end   = time.time()
    
    duration = pulse_end - pulse_start
    distance = duration * speed
    distance = round(distance, 2)
    
    LOGGER.debug("Distance: {0}cm".format(distance))
    
    return distance

try:
    startup()
    for i in range(0, 100):
        read_distance(SPEED_SOUND_CM)
        time.sleep(1)
finally:
    shutdown()