import os

from flask import Flask
from dotenv import load_dotenv
from routes.lstm_routes import lstm_routes
from models import db
from routes.meditation_routes import meditation_routes

app = Flask(__name__)
load_dotenv()

database_user = os.getenv('DATABASE_USER')
database_user_password = os.getenv('DATABASE_USER_PASSWORD')
database_name = os.getenv('DATABASE_NAME')

server_port = os.getenv('SERVER_PORT')
db_host = os.getenv("DATABASE_HOST", 'localhost')
app.config['SQLALCHEMY_DATABASE_URI'] = (f'mysql+pymysql://{database_user}:{database_user_password}@{db_host}/'
                                         f'{database_name}')
db.init_app(app)

# Set db and app in the app configuration
app.config['db'] = db
app.config['app'] = app

app.register_blueprint(lstm_routes)
app.register_blueprint(meditation_routes)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(port=server_port, debug=True, threaded=True, host='0.0.0.0')
