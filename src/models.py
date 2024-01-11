from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class MeditationSession(db.Model):
    __tablename__ = 'meditation_sessions'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(36), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    is_canceled = db.Column(db.Boolean, nullable=False, default=False)

    # Relationship to SessionPeriod
    session_periods = db.relationship('SessionPeriod', back_populates='meditation_session',
                                      cascade='all, delete-orphan')

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
    meditation_session_id = db.Column(db.Integer, db.ForeignKey('meditation_sessions.id', ondelete='CASCADE'),
                                      nullable=False)

    # Relationship to HeartRateMeasurement
    heart_rate_measurements = db.relationship('HeartRateMeasurement', back_populates='session_period',
                                              cascade='all, delete-orphan')

    # Relationship to MeditationSession
    meditation_session = db.relationship('MeditationSession', back_populates='session_periods')

    visualization = db.Column(db.String(255), nullable=True)
    beat_frequency = db.Column(db.Float, nullable=True)
    breathing_pattern = db.Column(db.JSON, nullable=False)
    breathing_pattern_multiplier = db.Column(db.Float, nullable=False)
    is_haptic_feedback_enabled = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'heartRateMeasurements': [measurement.to_dict() for measurement in self.heart_rate_measurements],
            'visualization': self.visualization,
            'beatFrequency': self.beat_frequency,
            'breathingPattern': self.breathing_pattern,
            'breathingPatternMultiplier': self.breathing_pattern_multiplier,
            'isHapticFeedbackEnabled': self.is_haptic_feedback_enabled
        }


class HeartRateMeasurement(db.Model):
    __tablename__ = 'heart_rate_measurements'
    id = db.Column(db.Integer, primary_key=True)
    session_period_id = db.Column(db.Integer, db.ForeignKey('session_periods.id', ondelete='CASCADE'), nullable=False)
    measurement_date = db.Column(db.DateTime, nullable=False)
    heart_rate = db.Column(db.Float, nullable=False)

    # Relationship to SessionPeriod
    session_period = db.relationship('SessionPeriod', back_populates='heart_rate_measurements')

    def to_dict(self):
        return {
            'date': self.measurement_date.isoformat(),
            'heartRate': self.heart_rate
        }
