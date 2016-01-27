import commands
from config import r

if __name__ == '__main__':
    while True:
        message = raw_input('Enter a command to execute: ')
        
        if commands.can_dispatch(message):        
            r.publish('rover', message)
        elif commands.execute(message) == False:
            break;