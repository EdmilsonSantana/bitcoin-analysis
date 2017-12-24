from flask import Flask, request
from flask_cors import CORS
from flask.json import jsonify
from helper import RepeatedTimer
from cryptocurrency_analysis import get_analysis, get_currencies
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

NOTIFICATION_TIMEOUT = 60
timers = {}

@socketio.on('request analysis data')
def request_analysis_data(json):
    sessionId = request.sid
    
    if(sessionId in timers):
        timer = timers[sessionId]
        timer.stop()
    
    time_frame = json["time_frame"]
    currency = json["currency"]
    periods = json["periods"]
    
    timers[request.sid] = RepeatedTimer(NOTIFICATION_TIMEOUT, 
                                          send_notification,
                                          sessionId,
                                          time_frame,
                                          periods,
                                          currency)

    send_notification(sessionId, time_frame, periods,currency)

def send_notification(sessionId, time_frame, periods, currency):
    
    df = get_analysis(time_frame, periods, currency)
    print(df)
    socketio.emit('get analysis data', 
                  df.to_json(orient='index',date_format='iso'), 
                  room=sessionId)
    
@socketio.on('connect')
def connect():
    print('Client %s connected.' % (request.sid))

@socketio.on('disconnect')
def disconnect():
    sessionId = request.sid
    if(sessionId in timers):
        timer = timers[sessionId]
        timer.stop()
        del timers[sessionId]
    print('Client %s disconnected.' % (sessionId))
    
@app.route('/currencies')
def currencies():
    return jsonify(get_currencies())

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
