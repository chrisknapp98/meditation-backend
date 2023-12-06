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
db_host = os.getenv("DATABASE_HOST", 'localhost')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{database_user}:{database_user_password}@{db_host}/{database_name}'
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
    required_fields = [
        'deviceId', 
        'date', 
        'duration', 
        'isCompleted', 
        'isCanceled', 
        'sessionPeriods',
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    required_fields_in_session_periods = [
        'heartRateMeasurements',
        'visualization',
        'beatFrequency',
        'breathingPattern', 
        'breathingPatternMultiplier', 
        'isHapticFeedbackEnabled', 
    ]
    for index, period in enumerate(data['sessionPeriods']):
        for field in required_fields_in_session_periods:
            if field not in period:
                return jsonify({'error': f'Missing required field: {field} in session period at index {index}'}), 400

    # Your logic to create a meditation session goes here...
    meditation_session = MeditationSession(
        device_id=data.get('deviceId'),
        date=datetime.strptime(data.get('date'), '%Y-%m-%dT%H:%M:%S.%fZ'),
        duration=data.get('duration'),
        is_completed=data.get('isCompleted'),
        is_canceled=data.get('isCanceled'),
        session_periods=[
            SessionPeriod(
                heart_rate_measurements=period.get('heartRateMeasurements'),
                visualization=period.get('visualization'),
                beat_frequency=period.get('beatFrequency'),
                breathing_pattern=period.get('breathingPattern'),
                breathing_pattern_multiplier=period.get('breathingPatternMultiplier'),
                is_haptic_feedback_enabled=period.get('isHapticFeedbackEnabled')
            ) for period in data.get('sessionPeriods')
        ]
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
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    is_canceled = db.Column(db.Boolean, nullable=False, default=False)
    session_periods = db.relationship('SessionPeriod', back_populates='meditation_session', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'deviceId': self.device_id,
            'date': self.date.isoformat() if self.date else None,
            'duration': self.duration,
            'isCompleted': self.is_completed,
            'isCanceled': self.is_canceled,
            'sessionPeriods': [period.to_dict() for period in self.session_periods]
        }


class SessionPeriod(db.Model):
    __tablename__ = 'session_periods'
    id = db.Column(db.Integer, primary_key=True)
    meditation_session_id = db.Column(db.Integer, db.ForeignKey('meditation_sessions.id', ondelete='CASCADE'), nullable=False)
    heart_rate_measurements = db.Column(db.JSON, nullable=False)
    visualization = db.Column(db.String(255), nullable=True)
    beat_frequency = db.Column(db.Float, nullable=True)
    breathing_pattern = db.Column(db.JSON, nullable=False)
    breathing_pattern_multiplier = db.Column(db.Float, nullable=False)
    is_haptic_feedback_enabled = db.Column(db.Boolean, nullable=False)

    meditation_session = db.relationship('MeditationSession', back_populates='session_periods')

    def to_dict(self):
        return {
            'heartRateMeasurements': self.heart_rate_measurements,
            'visualization': self.visualization,
            'beatFrequency': self.beat_frequency,
            'breathingPattern': self.breathing_pattern,
            'breathingPatternMultiplier': self.breathing_pattern_multiplier,
            'isHapticFeedbackEnabled': self.is_haptic_feedback_enabled
        }


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(port=server_port, debug=True, threaded=True, host='0.0.0.0')
