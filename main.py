from sockets import app, socketio

if __name__ == "__main__":
    socketio.run(app, host='163.221.68.234', port=5000, debug=True)
