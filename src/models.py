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

