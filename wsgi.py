from sockets import socketio, app

if __name__ == "__main__":
    socketio.run(app, host='163.221.68.234', port=5001, debug=False, use_reloader=False)
