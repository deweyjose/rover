import loggers
import time
import roboclaw

ADDRESS    = 0x80
DEVICE     = '/dev/ttyAMA0'
BAUD_RATE  = 115200
LOGGER     = loggers.get_logger(__file__, loggers.get_debug_level())
DIRFORWARD = "F"
DIRREVERSE = "R"
M1DIR      = DIRFORWARD
M2DIR      = DIRFORWARD
M1SPEED    = 0
M2SPEED    = 0

########################################################

def startup():
    LOGGER.debug("startup")
    LOGGER.debug("roboclaw.Open({0}, {1})".format(DEVICE, BAUD_RATE))
    roboclaw.Open(DEVICE, BAUD_RATE)
    return True

########################################################

def shutdown():    
    LOGGER.debug("shutdown")
    return True

########################################################
# Settings and Configurations
########################################################

class version(object):
    def __init__(self, ok, version):
        self.ok      = ok
        self.version = version

def get_version():
    LOGGER.debug("get_version")
    
    apival = roboclaw.ReadVersion(ADDRESS)
    
    LOGGER.debug("roboclaw.ReadVersion({0}) == {1}".format(ADDRESS, apival))
    
    if apival[0]==False:
        return version(apival[0], 'failed to read version')
    else:
        return version(apival[0], repr(apival[1]).replace("'", "").replace("\\n", ""))

########################################################
# SPEED
########################################################

class speed_and_direction(object):
    def __init__(self, speed_left, direction_left, speed_right, direction_right):
        self.speed_left      = speed_left
        self.speed_right     = speed_right
        self.direction_right = direction_right
        self.direction_left  = direction_left
        
        LOGGER.debug("speed_direction before {0} {1} {2} {3}".format(self.speed_left, self.direction_left, self.speed_right, self.direction_right))
    
    def asJSON(self):
        return {'speed':     {'right': self.speed_right    , 'left': self.speed_left    },
                'direction': {'right': self.direction_right, 'left': self.direction_left}}
            
            

def get_speed_and_direction():
    global M1SPEED, M1DIR, M2SPEED, M2DIR
    LOGGER.debug("speed_direction {0} {1} {2} {3}".format(M1SPEED, M1DIR, M2SPEED, M2DIR))
    return speed_and_direction(M1SPEED, M1DIR, M2SPEED, M2DIR)

########################################################
# ERRORS
########################################################

def get_errors():
    LOGGER.debug("get_errors")
    
    apival = roboclaw.ReadError(ADDRESS)
    
    LOGGER.debug("roboclaw.ReadError({0}) == {1}".format(ADDRESS, apival))
    
    ebitmask = apival[1]
    errors   = {}
    
    for bitmask in roboclaw.ERRORS:
        if bitmask & ebitmask == bitmask:
            errors[bitmask] = roboclaw.ERRORS.get(bitmask)
            LOGGER.debug("found {0} {1}".format(bitmask, errors[bitmask]))
            
    return errors

########################################################
# CONFIGURATION
########################################################

def get_configuration():
    LOGGER.debug("get_configuration")
    
    apival = roboclaw.GetConfig(ADDRESS)
    
    LOGGER.debug("roboclaw.GetConfig({0}) == {1}".format(ADDRESS, apival))
    
    cbitmask = apival[1]
    configuration = {}
    
    for bitmask in roboclaw.CONFIGURATION:
        if bitmask & cbitmask == bitmask:
            configuration[bitmask] = roboclaw.CONFIGURATION.get(bitmask)
            LOGGER.debug("found {0} {1}".format(bitmask, configuration[bitmask]))
    
    return configuration

########################################################
# VOLTAGE +-
########################################################

class voltage_settings(object):
    def __init__(self, main_min=None, main_max=None, logic_min=None, logic_max=None):
        self.main_min = main_min
        self.main_max = main_max
        self.logic_min = logic_min
        self.logic_max = logic_max    

def get_voltage_settings():
    LOGGER.debug("get_voltage_settings")
    
    main = roboclaw.ReadMinMaxMainVoltages(ADDRESS)
    
    LOGGER.debug("roboclaw.ReadMinMaxMainVoltages({0}) == {1}".format(ADDRESS, main))

    logic = roboclaw.ReadMinMaxLogicVoltages(ADDRESS)
    
    LOGGER.debug("roboclaw.ReadMinMaxLogicVoltages({0}) == {1}".format(ADDRESS, logic))
    
    return voltage_settings(main [1]/10, main [2]/10, logic[1]/10, logic[2]/10)

def set_voltage_settings(settings):
    LOGGER.debug("set_voltage_settings({0})".format(settings))
    
    if (settings.main_min != None):
        apival = roboclaw.SetMinVoltageMainBattery(ADDRESS, settings.main_min)
        LOGGER.debug("roboclaw.SetMinVoltageMainBattery({0}, {1}) == {2}".format(ADDRESS, settings.main_min, apival))
        if (apival == False): return False
    
    if (settings.main_max != None):
        apival = roboclaw.SetMaxVoltageMainBattery(ADDRESS, settings.main_max)
        LOGGER.debug("roboclaw.SetMaxVoltageMainBattery({0}, {1}) == {2}".format(ADDRESS, settings.main_max, apival))
        if (apival == False): return False
    
    if (settings.logic_max != None):
        apival = roboclaw.SetMaxVoltageLogicBattery(ADDRESS, settings.logic_max)
        LOGGER.debug("roboclaw.SetMaxVoltageLogicBattery({0}, {1}) == {2}".format(ADDRESS, settings.logic_max, apival))
        if (apival == False): return False

    if (settings.logic_min != None):
        apival = roboclaw.SetMinVoltageLogicBattery(ADDRESS, settings.logic_min)
        LOGGER.debug("roboclaw.SetMinVoltageLogicBattery({0}, {1}) == {2}".format(ADDRESS, settings.logic_min, apival))
        if (apival == False): return False
        
    return True
    
########################################################
# CURRENT
########################################################

class max_current_settings(object):
    def __init__(self, right, left):
        self.right = right
        self.left  = left    

def get_max_current_settings():
    LOGGER.debug("get_current_settings")
    
    M1 = roboclaw.ReadM1MaxCurrent(ADDRESS)
    
    LOGGER.debug("roboclaw.ReadM1MaxCurrent({0}) == {1}".format(ADDRESS, M1))
    
    M2 = roboclaw.ReadM2MaxCurrent(ADDRESS)
    
    LOGGER.debug("roboclaw.ReadM2MaxCurrent({0}) == {1}".format(ADDRESS, M2))
    
    return max_current_settings(M1[1]/100, M2[1]/100)

########################################################
# TEMPERATURE
########################################################

class temperature(object):
    def __init__(self, celsius, fahrenheit):
        self.celsius = celsius
        self.fahrenheit = fahrenheit

def get_temp():
    LOGGER.debug("get_temp")
    
    apival = roboclaw.ReadTemp(ADDRESS)
    
    LOGGER.debug("roboclaw.ReadTemp({0}) == {1}".format(ADDRESS, apival))
    
    celsius    = apival[1] / 10
    fahrenheit = (celsius * 1.8) + 32
    
    return temperature(celsius, fahrenheit)


########################################################
# MOVE
########################################################

def reverse_right(speed):
    global M2SPEED, M1DIR
    
    M1SPEED = speed
    M1DIR   = DIRREVERSE
    
    LOGGER.debug("reverse_right({0})".format(M1SPEED))
    
    apival = roboclaw.BackwardM1(ADDRESS, M1SPEED)
    
    LOGGER.debug("roboclaw.BackwardM1({0}, {1}) == {2}".format(ADDRESS, M1SPEED, apival))
    
    return apival
    
########################################################

def reverse_left(speed):
    global M2SPEED, M2DIR
        
    M2SPEED = speed
    M2DIR   = DIRREVERSE
    
    LOGGER.debug("reverse_left({0})".format(M2SPEED))

    apival = roboclaw.BackwardM2(ADDRESS, M2SPEED)
    
    LOGGER.debug("roboclaw.BackwardM2({0}, {1}) == {2}".format(ADDRESS, M2SPEED, apival))
    
    return apival

########################################################

def forward_right(speed):
    global M1SPEED, M1DIR
    
    M1SPEED = speed
    M1DIR   = DIRFORWARD
    
    LOGGER.debug("forward_right({0})".format(M1SPEED))

    apival = roboclaw.ForwardM1(ADDRESS, M1SPEED)
    
    LOGGER.debug("roboclaw.ForwardM1({0}, {1}) == {2}".format(ADDRESS, M1SPEED, apival))
    
    return apival

########################################################

def forward_left(speed):
    global M2SPEED, M2DIR
    
    M2SPEED = speed
    M2DIR   = DIRFORWARD
    
    LOGGER.debug("forward_left({0})".format(M2SPEED))

    apival = roboclaw.ForwardM2(ADDRESS, M2SPEED)
    
    LOGGER.debug("roboclaw.ForwardM2({0}, {1}) {2}".format(ADDRESS, M2SPEED, apival))
    
    return apival

########################################################

def apply_speed_adjustment():
    global M1SPEED, M2SPEED, M1DIR, M2DIR
    
    if M1DIR == DIRFORWARD:
        forward_right(M1SPEED)
    else:
        reverse_right(M1SPEED)
    
    if M2DIR == DIRFORWARD:
        forward_left(M2SPEED)
    else:
        reverse_left(M2SPEED)

########################################################
# DIRECTIONAL HELPERS
########################################################

def is_spinning():
    global M1DIR, M2DIR
    return M1DIR != M2DIR

def is_reverse():
    global M1DIR, M2DIR, DIRREVERSE
    return M1DIR == DIRREVERSE and M2DIR == DIRREVERSE

def is_forward():
    global M1DIR, M2DIR, DIRFORWARD
    return M1DIR == DIRFORWARD and M2DIR == DIRFORWARD

########################################################
# high level APIs
########################################################

def accelerate(amount=1):
    global M1SPEED, M2SPEED, M1DIR, M2DIR
    
    LOGGER.debug("accelerate({0})".format(amount))
    
    M1SPEED = min(127, M1SPEED + amount)
    M2SPEED = min(127, M2SPEED + amount)
    
    apply_speed_adjustment()
    return get_speed_and_direction()

########################################################

def decelerate(amount=1):
    global M1SPEED, M2SPEED, M1DIR, M2DIR
    
    LOGGER.debug("decelerate({0})".format(amount))
    
    M1SPEED = max(0, M1SPEED - amount)
    M2SPEED = max(0, M2SPEED - amount)
        
    apply_speed_adjustment()
    return get_speed_and_direction()

########################################################

def forward(amount=5):
    global M1SPEED, M2SPEED, M1DIR, M2DIR
    LOGGER.debug("forward")
        
    if is_forward():
        accelerate(amount)
    else:
        stop()
        forward_right(max(M1SPEED, M2SPEED))
        forward_left (max(M1SPEED, M2SPEED))
        accelerate()    
    
    return get_speed_and_direction()

########################################################

def reverse(amount=5):
    global M1SPEED, M2SPEED, M1DIR, M2DIR
    LOGGER.debug("reverse")
    
    if is_reverse():
        accelerate(amount)
    else:
        stop()
        reverse_right(max(M1SPEED, M2SPEED))
        reverse_left (max(M1SPEED, M2SPEED))
    
    return get_speed_and_direction()

########################################################

def stop(deceleration=50):
    global M1SPEED, M2SPEED
    
    LOGGER.debug("stop({0})".format(deceleration))
    
    while M1SPEED > 0 or M2SPEED > 0:
        decelerate(deceleration)
        time.sleep(0.5)
    
    return get_speed_and_direction()

########################################################

def spin(clockwise=True):
    global M1SPEED, M2SPEED
    
    LOGGER.debug("spin({0})".format(clockwise))
    
    spin_speed = max(M1SPEED, M2SPEED)
    
    if is_spinning() == False:
        stop()
    
    if clockwise == True:
        forward_left (spin_speed)
        reverse_right(spin_speed)        
    else:
        forward_right(spin_speed)
        reverse_left (spin_speed)
    
    return get_speed_and_direction()

########################################################

def turn_left(sharpness=3):
    global M1SPEED, M2SPEED
    LOGGER.debug("turn_left({0})".format(sharpness))    
    forward_left (max(0, M1SPEED/sharpness))
    return get_speed_and_direction()

########################################################

def turn_right(sharpness=3):
    LOGGER.debug("turn_right({0}))".format(sharpness))
    forward_right(max(0, M2SPEED/sharpness))
    return get_speed_and_direction()
    