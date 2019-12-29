import loggers
import time
import roboclaw

ADDRESS    = 0x80
DEVICE     = '/dev/ttyAMA0'
BAUD_RATE  = 115200
LOGGER     = loggers.get_logger(__file__, loggers.get_default_level())
DIRFORWARD = "F"
DIRREVERSE = "R"
RIGHTDIR   = DIRFORWARD
LEFTDIR    = DIRFORWARD
RIGHTSPEED = 0
LEFTSPEED  = 0
MAX_SPEED  = 127
MIN_SPEED  = 0

########################################################

def startup():
    LOGGER.debug("startup")
    LOGGER.debug("roboclaw.Open({0}, {1})".format(DEVICE, BAUD_RATE))    
    roboclaw.Open(DEVICE, BAUD_RATE)
    set_voltage_settings(voltage_settings(0))
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
    global RIGHTSPEED, RIGHTDIR, LEFTSPEED, LEFTDIR
    LOGGER.debug("speed_direction {0} {1} {2} {3}".format(RIGHTSPEED, RIGHTDIR, LEFTSPEED, LEFTDIR))
    return speed_and_direction(RIGHTSPEED, RIGHTDIR, LEFTSPEED, LEFTDIR)

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
    global RIGHTSPEED, RIGHTDIR
    
    RIGHTSPEED = max(MIN_SPEED, min(MAX_SPEED, speed))
    RIGHTDIR   = DIRREVERSE
    
    LOGGER.debug("reverse_right({0})".format(RIGHTSPEED))
    
    apival = roboclaw.BackwardM1(ADDRESS, RIGHTSPEED)
    
    LOGGER.debug("roboclaw.BackwardM1({0}, {1}) == {2}".format(ADDRESS, RIGHTSPEED, apival))
    
    return apival
    
########################################################

def reverse_left(speed):
    global LEFTSPEED, LEFTDIR
        
    LEFTSPEED = max(MIN_SPEED, min(MAX_SPEED, speed))
    LEFTDIR   = DIRREVERSE
    
    LOGGER.debug("reverse_left({0})".format(LEFTSPEED))

    apival = roboclaw.BackwardM2(ADDRESS, LEFTSPEED)
    
    LOGGER.debug("roboclaw.BackwardM2({0}, {1}) == {2}".format(ADDRESS, LEFTSPEED, apival))
    
    return apival

########################################################

def forward_right(speed):
    global RIGHTSPEED, RIGHTDIR
    
    RIGHTSPEED = max(MIN_SPEED, min(MAX_SPEED, speed))
    RIGHTDIR   = DIRFORWARD
    
    LOGGER.debug("forward_right({0})".format(RIGHTSPEED))

    apival = roboclaw.ForwardM1(ADDRESS, RIGHTSPEED)
    
    LOGGER.debug("roboclaw.ForwardM1({0}, {1}) == {2}".format(ADDRESS, RIGHTSPEED, apival))
    
    return apival

########################################################

def forward_left(speed):
    global LEFTSPEED, LEFTDIR
    
    LEFTSPEED = max(MIN_SPEED, min(MAX_SPEED, speed))
    LEFTDIR   = DIRFORWARD
    
    LOGGER.debug("forward_left({0})".format(LEFTSPEED))

    apival = roboclaw.ForwardM2(ADDRESS, LEFTSPEED)
    
    LOGGER.debug("roboclaw.ForwardM2({0}, {1}) {2}".format(ADDRESS, LEFTSPEED, apival))
    
    return apival

########################################################

def apply_speed_adjustment():
    global RIGHTSPEED, LEFTSPEED, RIGHTDIR, LEFTDIR
    
    if RIGHTDIR == DIRFORWARD:
        forward_right(RIGHTSPEED)
    else:
        reverse_right(RIGHTSPEED)
    
    if LEFTDIR == DIRFORWARD:
        forward_left(LEFTSPEED)
    else:
        reverse_left(LEFTSPEED)

########################################################
# DIRECTIONAL HELPERS
########################################################

def is_spinning():
    global RIGHTDIR, LEFTDIR
    return RIGHTDIR != LEFTDIR

def is_reverse():
    global RIGHTDIR, LEFTDIR, DIRREVERSE
    return RIGHTDIR == DIRREVERSE and LEFTDIR == DIRREVERSE

def is_forward():
    global RIGHTDIR, LEFTDIR, DIRFORWARD
    return RIGHTDIR == DIRFORWARD and LEFTDIR == DIRFORWARD

def is_turning():
    global RIGHTSPEED, LEFTSPEED
    return RIGHTSPEED != LEFTSPEED

########################################################
# high level APIs
########################################################

def accelerate(amount=5):
    global RIGHTSPEED, LEFTSPEED, RIGHTDIR, LEFTDIR
    
    LOGGER.debug("accelerate({0})".format(amount))
    
    RIGHTSPEED = min(MAX_SPEED, RIGHTSPEED + amount)
    LEFTSPEED = min(MAX_SPEED, LEFTSPEED + amount)
    
    apply_speed_adjustment()
    return get_speed_and_direction()

########################################################

def decelerate(amount=5):
    global RIGHTSPEED, LEFTSPEED, RIGHTDIR, LEFTDIR
    
    LOGGER.debug("decelerate({0})".format(amount))
    
    RIGHTSPEED = max(MIN_SPEED, RIGHTSPEED - amount)
    LEFTSPEED = max(MIN_SPEED, LEFTSPEED - amount)
        
    apply_speed_adjustment()
    return get_speed_and_direction()

########################################################

def forward(amount=10):
    global RIGHTSPEED, LEFTSPEED, RIGHTDIR, LEFTDIR
    LOGGER.debug("forward")
        
    if is_forward() == False:
        stop()
   
    can_accelerate = is_turning() == False
    
    forward_right(max(RIGHTSPEED, LEFTSPEED))
    forward_left (max(RIGHTSPEED, LEFTSPEED))
    
    if can_accelerate == True:
        accelerate(amount)
    
    return get_speed_and_direction()

########################################################

def reverse(amount=10):
    global RIGHTSPEED, LEFTSPEED, RIGHTDIR, LEFTDIR
    LOGGER.debug("reverse")
    
    if is_reverse() == False:
        stop()
    
    can_accelerate = is_turning() == False
    reverse_right(max(RIGHTSPEED, LEFTSPEED))
    reverse_left (max(RIGHTSPEED, LEFTSPEED))
    
    if can_accelerate == True:
        accelerate(amount)
    
    return get_speed_and_direction()

########################################################

def stop(deceleration=50):
    global RIGHTSPEED, LEFTSPEED
    
    LOGGER.debug("stop({0})".format(deceleration))
    
    while RIGHTSPEED > MIN_SPEED or LEFTSPEED > MIN_SPEED:
        decelerate(deceleration)
        time.sleep(0.5)
    
    return get_speed_and_direction()

def stop_forward(deceleration=50):
    if is_forward():
        stop(MAX_SPEED)

def stop_reverse(deceleration=50):
    if is_reverse():
        stop(MAX_SPEED)

########################################################

def spin(clockwise=True):
    global RIGHTSPEED, LEFTSPEED
    
    LOGGER.debug("spin({0})".format(clockwise))
    
    spin_speed = max(RIGHTSPEED, LEFTSPEED)
    
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

def turn(sharpness,
         speed1, speed2,
         forward_turn_func,
         forward_turn_faster_func,
         forward_straighten_func,
         reverse_turn_func,
         reverse_turn_faster_func,
         reverse_straighten_func
         ):
    global RIGHTSPEED, LEFTSPEED
    LOGGER.debug("turn({0})".format(sharpness))
    
    if is_forward():
        turn_func        = forward_turn_func
        turn_faster_func = forward_turn_faster_func
        straighten_func  = forward_straighten_func
    else:
        turn_func        = reverse_turn_func
        turn_faster_func = reverse_turn_faster_func
        straighten_func  = reverse_straighten_func
    
    if speed1 == speed2:
        turn_func(max(MIN_SPEED, speed1/sharpness))
    elif speed1 < speed2:
        straighten_func()
        time.sleep(0.3)
        turn_func(max(MIN_SPEED, speed1/sharpness))
    else:
        turn_faster_func(min(MAX_SPEED, int(speed1*1.3)))        
    
    return get_speed_and_direction()

########################################################

def turn_left(sharpness=3):
    return turn(sharpness, RIGHTSPEED, LEFTSPEED, forward_left, forward_right, forward, reverse_left, reverse_right, reverse)    

########################################################

def turn_right(sharpness=3):
    return turn(sharpness, LEFTSPEED, RIGHTSPEED, forward_right, forward_left, forward, reverse_right, reverse_left, reverse)    

########################################################

def get_diagnostics_info():
    version     = get_version()
    voltage     = get_voltage_settings()
    current     = get_max_current_settings()
    temperature = get_temp()
    errors      = get_errors()
    config      = get_configuration()
    speed       = get_speed_and_direction()
    
    info = [{'name':'version'          , 'value': version.version       },
            {'name':'main max voltage' , 'value': voltage.main_max      },
            {'name':'main min voltage' , 'value': voltage.main_min      },
            {'name':'logic max voltage', 'value': voltage.logic_max     },
            {'name':'logic min voltage', 'value': voltage.logic_min     },
            {'name':'max current right', 'value': current.right         },
            {'name':'max current left' , 'value': current.left          },
            {'name':'temp fahrenheit'  , 'value': temperature.fahrenheit},
            {'name':'temp celsius'     , 'value': temperature.celsius   },
            {'name':'errors'           , 'value': errors.values()       },
            {'name':'right speed'      , 'value': speed.speed_right     },
            {'name':'right direction'  , 'value': speed.direction_right },
            {'name':'left speed'       , 'value': speed.speed_left      },
            {'name':'left direction'   , 'value': speed.direction_left  }]
    
    for key in config:
        info.append({'name': config.get(key), 'value': key})
    
    return info

#######################################################

CMD_MAPPING = {'forward'     : forward,
               'f'           : forward,
               'reverse'     : reverse,
               'b'           : reverse,
               'left'        : turn_left,
               'l'           : turn_left,
               'right'       : turn_right,
               'r'           : turn_right,
               'spin'        : spin,
               's'           : spin,
               'stop'        : stop,
               'x'           : stop,
               'stop_forward': stop_forward,
               'stop_reverse': stop_reverse,
               'accelerate'  : accelerate,
               'a'           : accelerate,
               'decelerate'  : decelerate,
               'd'           : decelerate,
               'diagnostics' : get_diagnostics_info,
               'z'           : get_diagnostics_info}

def execute_command(cmd):
    if cmd == 'help' or cmd == 'h':
        LOGGER.info("FUNCTIONS: %s" % ' '.join(CMD_MAPPING.keys()))
    elif cmd == 'quit' or cmd == 'q':
        LOGGER.info("good bye!")
        return False
    else:
        func_info = CMD_MAPPING.get(cmd)

        if func_info == None:
            LOGGER.error("Unknown command %s" % cmd)
        else:
            func = func_info
            if func != None:
                func()

    return True

