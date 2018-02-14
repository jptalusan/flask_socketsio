from sockets import app, socketio, db
from sockets import mqtt
import threading
from datetime import datetime
from sockets.models import Masternode, Slavenode

def do_every (interval, worker_func, iterations = 0):
  if iterations != 1:
    threading.Timer (
      interval,
      do_every, [interval, worker_func, 0 if iterations == 0 else iterations-1]
    ).start ()

  worker_func ()

def show_time ():
  time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  mqtt.publish('hello/world', time)

if __name__ == "__main__":
    do_every(5, show_time)
    socketio.run(app, host='163.221.68.224', port=5001, debug=True, use_reloader=False)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Masternode': Masternode, 'Slavenode': Slavenode}
