import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from routes.lstm_routes import predict, train_model

app = Flask(__name__)
load_dotenv()

server_port = 5001

# database configuration
database_user = os.getenv('DATABASE_USER')
database_user_password = os.getenv('DATABASE_USER_PASSWORD')
database_name = os.getenv('DATABASE_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{database_user}:{database_user_password}@localhost/{database_name}'
db = SQLAlchemy(app)
app.config['db'] = db
app.config['app'] = app

# register lstm routes
app.add_url_rule('/predict', view_func=predict, methods=['POST'])
app.add_url_rule('/train_model', view_func=train_model, methods=['POST'])

# register meditation routes
#app.add_url_rule('/meditations', view_func=get_meditation_sessions, methods=['GET'])
#app.add_url_rule('/meditations', view_func=create_meditation_session, methods=['POST'])

if __name__ == '__main__':
    app.run(port=server_port, debug=True, threaded=True, host='0.0.0.0') 


