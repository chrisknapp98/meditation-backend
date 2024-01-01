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

    required_fields_in_heart_rate_measurements = [
        'date',
        'heartRate',
    ]
    for index, period in enumerate(data['sessionPeriods']):
        for index2, measurement in enumerate(period['heartRateMeasurements']):
            for field in required_fields_in_heart_rate_measurements:
                if field not in measurement:
                    return jsonify({'error': f'Missing required field: {field} in heart rate measurement at index {index2} in session period at index {index}'}), 400

    # Your logic to create a meditation session goes here...
    meditation_session = MeditationSession(
        device_id=data.get('deviceId'),
        date=datetime.strptime(data.get('date'), '%Y-%m-%dT%H:%M:%S.%fZ'),
        duration=data.get('duration'),
        is_completed=data.get('isCompleted'),
        is_canceled=data.get('isCanceled'),
        session_periods=[
            SessionPeriod(
                heart_rate_measurements=[
                    HeartRateMeasurement(
                        measurement_date=datetime.strptime(measurement.get('date'), '%Y-%m-%dT%H:%M:%S.%fZ'),
                        heart_rate=measurement.get('heartRate')
                    ) for measurement in period.get('heartRateMeasurements')
                ],
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


