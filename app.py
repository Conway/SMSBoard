from flask import Flask, abort, render_template, request
from flask_socketio import SocketIO
from netaddr import IPNetwork, IPAddress
import json
import os
import redis

app = Flask(__name__)
app.config['SECRET_KEY'] = "jhadgkuyeg23(*Y87TRI&#jhfds" #changeme before using!
app.config['NUMBER'] = os.environ.get('NUMBER')
app.debug = True
redis = redis.from_url(os.environ.get("REDIS_URL"))
socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template('listing.html', async_mode=socketio.async_mode)

@socketio.on('connect', namespace='/soc')
def increment():
    count = redis.incr('connected')
    if count == 0:
        count = 1
    socketio.emit('count', {'count': count}, namespace='/soc')

@socketio.on('disconnect', namespace='/soc')
def decrement():
    count = redis.decr('connected')
    if count == 0:
        count = 1
    socketio.emit('count', {'count': count+1}, namespace='/soc')

@app.route('/message', methods=['GET'])
def POST_message():
    # check to make sure request is actually coming from Nexmo
    if 'X-Forwarded-For' in request.headers:
        remote_addr = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        remote_addr = request.remote_addr or 'untrackable'
    if not verify_ip(remote_addr):
        return abort(403)
    message = str(request.args.get('text'))
    sender = str(request.args.get('msisdn'))
    sender_id = redis.get(sender)
    if not sender_id or sender_id == None:
        id = redis.incr("id")
        sender_id = str("user" + str(id))
        redis.set(sender, sender_id)
    else:
        sender_id = str(sender_id)
        sender_id = sender_id[2:len(sender_id)-1]
    socketio.emit('message', {'message': message, 'sender':sender_id}, namespace="/soc")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

def verify_ip(ip):
    allowed_ips = ['174.37.245.32/29', '174.36.197.192/28', '173.193.199.16/28', '119.81.44.0/28']
    for allowed_ip in allowed_ips:
        if IPAddress(str(ip)) in IPNetwork(allowed_ip):
            return True
    return False

if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", port=5000)
