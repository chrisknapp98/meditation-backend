import os
import numpy as np
from datetime import datetime

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

import lstm.meditation_lstm as meditation_lstm
from routes.lstm_routes import test, predict, train_model

#from routes.meditation_routes import get_meditation_sessions, create_meditation_session

app = Flask(__name__)
load_dotenv()

database_user = os.getenv('DATABASE_USER')
database_user_password = os.getenv('DATABASE_USER_PASSWORD')
database_name = os.getenv('DATABASE_NAME')

#server_port = os.getenv('SERVER_PORT')
server_port = 5001

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{database_user}:{database_user_password}@localhost/{database_name}'
db = SQLAlchemy(app)

# Set db and app in the app configuration
app.config['db'] = db
app.config['app'] = app

# Register lstm routes
app.add_url_rule('/test', view_func=test, methods=['GET'])
app.add_url_rule('/predict', view_func=predict, methods=['GET'])
app.add_url_rule('/train_model', view_func=train_model, methods=['POST'])

# TODO: Register meditation routes
#app.add_url_rule('/meditations', view_func=get_meditation_sessions, methods=['GET'])
#app.add_url_rule('/meditations', view_func=create_meditation_session, methods=['POST'])

if __name__ == '__main__':
    app.run(port=server_port, debug=True, threaded=True, host='0.0.0.0') 


