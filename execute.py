import commands
from settings import rconn

if __name__ == '__main__':
    while True:
        message = raw_input('Enter a command to execute: ')
        
        if commands.can_dispatch(message):        
            rconn.publish('rover', message)
        elif commands.execute(message) == False:
            break;
