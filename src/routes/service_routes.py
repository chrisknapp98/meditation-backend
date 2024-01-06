import sqlalchemy
from flask import Blueprint
from flask import jsonify

service_routes = Blueprint('service_routes', __name__)
from models import MeditationSession


@service_routes.route("/ready", methods=['GET'])
def get_meditation_sessions():
    # check whether database is reachable
    try:
        MeditationSession.query.all()
    except sqlalchemy.exc.OperationalError:
        return jsonify({'error': 'database not reachable'}), 503
    return jsonify({'message': 'server is ready'}), 200
