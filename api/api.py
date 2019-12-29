import loggers
import motorctrl
from flask import Flask, render_template, request, jsonify

LOGGER = loggers.get_logger(__file__)
 
app = Flask(__name__)

def initialize(app):
    LOGGER.info("Initializing Motorcontroller...")
    motorctrl.startup()

def publish(command):
    return { "command": command,
             "result": motorctrl.execute_command(command) } 

initialize(app)

@app.route('/')
def index():
    return render_template('drive.html')

@app.route('/accelerate')
def accelerate():
    return publish("accelerate")
   
@app.route('/decelerate')
def decelerate():    
    return publish("decelerate")

@app.route('/forward')
def forward():    
    return publish('forward')

@app.route('/reverse')
def reverse():    
    return publish('reverse')

@app.route('/stop')
def stop():    
    return publish('stop')

@app.route('/right')
def right():    
    return publish('right')

@app.route('/left')
def left():    
    return publish('left')

@app.route('/spin')
def spin():    
    return publish('spin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int("8888"))
    
