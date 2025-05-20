#!/bin/env python
from app import create_app, socketio
import os
import db too if using the in app context()

app = create_app(debug=True, host='0.0.0.0')

with app.app_context():
    db.create_all()
#unnecessary change

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
