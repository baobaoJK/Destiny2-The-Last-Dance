from utils import socketio, app

import controllers
from utils.load_config import load_config


@app.route('/')
def hello_world():  # put application's code here
    return 'Destiny2!'

if __name__ == '__main__':
    config = load_config()
    socketio.run(app, host=config['server']['host'], port=config['server']['port'], debug=config['server']['debug'])
