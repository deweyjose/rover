import diagnostics
import motorctrl
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

motorctrl.startup()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/joystick')
def joystick():
    return render_template('joystick.html')

@app.route('/diagnostics')
def diagnosticsx():
    return render_template('diagnostics.html', attributes=diagnostics.get_info_dictionary())

@app.route('/logs')
def logs():
    return render_template('logs.html')

@app.route('/drive')
def drive():
    return render_template('drive.html')

@app.route('/accelerate')
def accelerate():    
    return jsonify(result=motorctrl.accelerate(15).asJSON());
    
@app.route('/decelerate')
def decelerate():    
    return jsonify(result=motorctrl.decelerate(15).asJSON());

@app.route('/forward')
def forward():    
    return jsonify(result=motorctrl.forward(15).asJSON());

@app.route('/reverse')
def reverse():    
    return jsonify(result=motorctrl.reverse(15).asJSON());

@app.route('/stop')
def stop():    
    return jsonify(result=motorctrl.stop(127).asJSON());

@app.route('/right')
def right():    
    return jsonify(result=motorctrl.turn_right().asJSON());

@app.route('/left')
def left():    
    return jsonify(result=motorctrl.turn_left().asJSON());

@app.route('/spin')
def spin():    
    return jsonify(result=motorctrl.spin().asJSON());

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int("8888"))