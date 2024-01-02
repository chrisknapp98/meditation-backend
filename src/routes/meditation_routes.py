from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import current_app, request, jsonify

from models import HeartRateMeasurement, MeditationSession, SessionPeriod

meditation_routes = Blueprint('meditation_routes', __name__)


@meditation_routes.route("/meditations", methods=['GET'])
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

        result = {'meditationSessions': []}
        for session in meditation_sessions:
            result['meditationSessions'].append(session.to_dict())

        return jsonify(result)

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


@meditation_routes.route("/meditations", methods=['POST'])
def create_meditation_session():
    db = current_app.config['db']

    # Validate the request body
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request body'}), 400

    validated_data, error = validate_meditation_session_data(data)
    if error:
        error_message, status_code = error
        return jsonify(error_message), status_code

    # Your logic to create a meditation session goes here...
    meditation_session = create_meditation_session_from_data(validated_data)

    db.session.add(meditation_session)
    db.session.commit()

    return jsonify({'message': 'Meditation session created successfully'}), 201


def validate_meditation_session_data(data):
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
            return None, ({'error': f'Missing required field: {field}'}, 400)

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
                return None, ({'error': f'Missing required field: {field} in session period at index {index}'}, 400)

        required_fields_in_heart_rate_measurements = [
            'date',
            'heartRate',
        ]
        for index2, measurement in enumerate(period['heartRateMeasurements']):
            for field in required_fields_in_heart_rate_measurements:
                if field not in measurement:
                    return None, ({'error': f'Missing required field: {field} in heart rate measurement at index {index2} in session period at index {index}'}, 400)

    return data, None

def create_meditation_session_from_data(data):
    return MeditationSession(
        device_id=data['deviceId'],
        date=datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S.%fZ'),
        duration=data['duration'],
        is_completed=data['isCompleted'],
        is_canceled=data['isCanceled'],
        session_periods=[
            SessionPeriod(
                heart_rate_measurements=[
                    HeartRateMeasurement(
                        measurement_date=datetime.strptime(measurement['date'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                        heart_rate=measurement['heartRate']
                    ) for measurement in period['heartRateMeasurements']
                ],
                visualization=period['visualization'],
                beat_frequency=period['beatFrequency'],
                breathing_pattern=period['breathingPattern'],
                breathing_pattern_multiplier=period['breathingPatternMultiplier'],
                is_haptic_feedback_enabled=period['isHapticFeedbackEnabled']
            ) for period in data['sessionPeriods']
        ]
    )

def get_last_session_from_db(device_id):
    db = current_app.config['db']
    session = db.session.query(MeditationSession).filter_by(device_id=device_id).order_by(MeditationSession.date.desc()).first()
    return session

def remove_session_from_db(session):
    db = current_app.config['db']
    device_id = session['device_id']
    date = session['date']
    found_session = db.session.query(MeditationSession).filter_by(device_id=device_id).order_by(MeditationSession.date.desc()).first()
    if found_session.to_dict()['date'] == date:
        db.session.delete(found_session)
        db.session.commit()

def save_session_to_db(session):
    db = current_app.config['db']
    session_model = create_meditation_session_from_data(session)
    db.session.add(session_model)
    db.session.commit()

def get_all_sessions_from_db(device_id):
    db = current_app.config['db']
    sessions = db.session.query(MeditationSession).filter_by(device_id=device_id).all()
    return sessions