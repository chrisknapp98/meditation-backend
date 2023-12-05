from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

database_user = os.getenv('DATABASE_USER')
database_user_password = os.getenv('DATABASE_USER_PASSWORD')
database_name = os.getenv('DATABASE_NAME')

server_port = os.getenv('SERVER_PORT')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{database_user}:{database_user_password}@localhost/{database_name}'
db = SQLAlchemy(app)

@app.route('/predict', methods=['POST'])
def predict():
    # Parse JSON data from the request body
    data = request.json

    # Your model prediction logic here
    result = {"prediction": "some_result"}

    # Return the result as JSON
    return jsonify(result)

@app.route('/meditations', methods=['GET'])
def get_meditation_sessions():
    try:
        # Get device_id from query parameters
        device_id = request.args.get('deviceId')

        # Use joinedload to eager load the related SessionMeta
        query = MeditationSession.query

        # Filter by device_id if provided
        if device_id:
            query = query.filter_by(device_id=device_id)

        # Execute the query
        meditation_sessions = query.all()

        if not meditation_sessions:
            return jsonify({'message': 'No meditation sessions found'}), 404

        result = {'meditation_sessions': []}
        for session in meditation_sessions:
            result['meditation_sessions'].append(session.to_dict())

        return jsonify(result)

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/meditation', methods=['POST'])
def create_meditation_session():
    # Validate the request body
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request body'}), 400

    # Validate required fields in the request body
    required_fields = ['deviceId', 'date', 'duration', 'heartRateMeasurements', 'sessionMeta']
    required_fields_in_session_meta = ['isHapticFeedbackEnabled', 'breathingPattern', 'breathingPatternMultiplier']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    for field in required_fields_in_session_meta:
        if field not in data['sessionMeta']:
            return jsonify({'error': f'Missing required field: {field} in sessionMeta'}), 400

    # Your logic to create a meditation session goes here...
    meditation_session = MeditationSession(
    device_id = data.get('deviceId'),
    date = datetime.strptime(data.get('date'), '%Y-%m-%dT%H:%M:%S.%fZ'),
    duration = data.get('duration'),
    time_until_relaxation = data.get('timeUntilRelaxation'),
    min_heart_rate = data.get('minHeartRate'),
    max_heart_rate = data.get('maxHeartRate'),
    avg_heart_rate = data.get('avgHeartRate'),
    heart_rate_measurements = data.get('heartRateMeasurements'),
    session_meta = SessionMeta(
        is_haptic_feedback_enabled = data['sessionMeta'].get('isHapticFeedbackEnabled'),
        sound = data['sessionMeta'].get('sound'),
        ambient = data['sessionMeta'].get('ambient'),
        mandala = data['sessionMeta'].get('mandala'),
        breathing_pattern = data['sessionMeta'].get('breathingPattern'),
        breathing_pattern_multiplier = data['sessionMeta'].get('breathingPatternMultiplier')
    )
)

    # Add the meditation session to the database
    db.session.add(meditation_session)
    db.session.commit()

    return jsonify({'message': 'Meditation session created successfully'}), 201


class MeditationSession(db.Model):
    __tablename__ = 'meditation_sessions'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(36), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    time_until_relaxation = db.Column(db.Integer, nullable=True)
    min_heart_rate = db.Column(db.Integer, nullable=True)
    max_heart_rate = db.Column(db.Integer, nullable=True)
    avg_heart_rate = db.Column(db.Integer, nullable=True)
    heart_rate_measurements = db.Column(db.JSON, nullable=False)
    session_meta_id = db.Column(db.Integer, db.ForeignKey('session_meta.id'), nullable=False)
    session_meta = db.relationship('SessionMeta', back_populates='meditation_sessions', uselist=False)

    def to_dict(self):
        return {
            'session': {
                'deviceId': self.device_id,
                'date': self.date.isoformat() if self.date else None,
                'duration': self.duration,
                'timeUntilRelaxation': self.time_until_relaxation,
                'minHeartRate': self.min_heart_rate,
                'maxHeartRate': self.max_heart_rate,
                'avgHeartRate': self.avg_heart_rate,
                'heartRateMeasurements': self.heart_rate_measurements,
                'sessionMeta': self.session_meta.to_dict() if self.session_meta else None
            },
        }

class SessionMeta(db.Model):
    __tablename__ = 'session_meta'
    id = db.Column(db.Integer, primary_key=True)
    is_haptic_feedback_enabled = db.Column(db.Boolean, nullable=False)
    sound = db.Column(db.String(255), nullable=True)
    ambient = db.Column(db.String(255), nullable=True)
    mandala = db.Column(db.String(255), nullable=True)
    breathing_pattern = db.Column(db.JSON, nullable=False)  # Use JSON type for breathing pattern
    breathing_pattern_multiplier = db.Column(db.Integer, nullable=False)
    meditation_sessions = db.relationship('MeditationSession', back_populates='session_meta', uselist=False)

    def to_dict(self):
        return {
            'isHapticFeedbackEnabled': self.is_haptic_feedback_enabled,
            'sound': self.sound,
            'ambient': self.ambient,
            'mandala': self.mandala,
            'breathingPattern': self.breathing_pattern,
            'breathingPatternMultiplier': self.breathing_pattern_multiplier
        }



if __name__ == '__main__':

    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()

    app.run(port=server_port, debug=True, threaded=True, host='0.0.0.0') 
