from flask import Flask, request
from helper import RepeatedTimer
from bitcoin_analysis import get_analysis
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b59b8546b80177dab45e2959dd5b2007'
socketio = SocketIO(app)

NOTIFICATION_TIMEOUT = 15
timers = {}

@socketio.on('request analysis data')
def request_analysis_data(json):
    sessionId = request.sid
    
    if(sessionId in timers):
        timer = timers[sessionId]
        timer.stop()
        
    timers[request.sid] = RepeatedTimer(NOTIFICATION_TIMEOUT, 
                                          send_notification,
                                          sessionId,
                                          json["freq"],
                                          json["periods"])

    send_notification(sessionId, json["freq"], json["periods"])

def send_notification(sessionId, freq, periods):
    df = get_analysis(freq, periods)
    socketio.emit('get analysis data', df.to_json(orient='index',date_format='iso'), room=sessionId)
    
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

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
