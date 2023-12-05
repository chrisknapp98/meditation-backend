from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://middleware:supersafepassword@localhost/meditation_db'
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
    # Retrieve all meditation sessions from the database
    meditation_sessions = MeditationSession.query.all()

    # Convert the sessions to a list of dictionaries
    result = [session.to_dict() for session in meditation_sessions]

    # Return the result as JSON
    return jsonify(result)

@app.route('/meditation', methods=['POST'])
def create_meditation_session():
    # Parse JSON data from the request body
    data = request.json

    # Create a new meditation session
    session = MeditationSession(title=data['title'], duration=data['duration'])
    
    # Add the session to the database
    db.session.add(session)
    db.session.commit()

    # return success string 
    return "Successfully saved meditation session."

class MeditationSession(db.Model):
    __tablename__ = 'meditation_sessions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }



# Run on port 5001
if __name__ == '__main__':
    app.run(port=5001, debug=True, threaded=True, host='0.0.0.0') 
