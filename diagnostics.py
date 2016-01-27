import motorctrl
import loggers

LOGGER = loggers.get_logger(__file__, loggers.get_default_level())

def print_info_dictionary():
    LOGGER.info("{0}".format(get_info_dictionary()))
    
def get_info_dictionary():
    version = motorctrl.get_version()
    if version.ok == False:
        return None
    
    voltage     = motorctrl.get_voltage_settings()
    current     = motorctrl.get_max_current_settings()
    temperature = motorctrl.get_temp()
    errors      = motorctrl.get_errors()
    config      = motorctrl.get_configuration()
    speed       = motorctrl.get_speed_and_direction()
        
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
    
