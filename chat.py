#!/bin/env python
from app import create_app, socketio
#import db too if using the in app context()

app = create_app(debug=True, host='0.0.0.0')

#with app.app_context():
#    db.create_all()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000)
    socketio.run(app, host='192.168.126.2', port=3000)