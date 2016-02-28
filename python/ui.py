from settings import rconn
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def publish(command):
    rconn.publish('rover', command)

@app.route('/')
def index():
    return render_template('drive.html')

@app.route('/accelerate')
def accelerate():
    publish("accelerate")
    return jsonify(result='ok');
    
@app.route('/decelerate')
def decelerate():    
    publish("decelerate")
    return jsonify(result='ok');

@app.route('/forward')
def forward():    
    publish('forward')
    return jsonify(result='ok');

@app.route('/reverse')
def reverse():    
    publish('reverse')
    return jsonify(result='ok');

@app.route('/stop')
def stop():    
    publish('stop')
    return jsonify(result='ok');

@app.route('/right')
def right():    
    publish('right')
    return jsonify(result='ok');

@app.route('/left')
def left():    
    publish('left')
    return jsonify(result='ok');

@app.route('/spin')
def spin():    
    publish('spin')
    return jsonify(result='ok');

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int("8888"))
    