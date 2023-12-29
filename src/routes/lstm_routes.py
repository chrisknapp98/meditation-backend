from flask import request, jsonify, Blueprint
import numpy as np
import lstm.meditation_lstm as meditation_lstm

lstm_routes = Blueprint('lstm_routes', __name__)

# This route predicts the next best session configuration (combination of binaural beats, visualization and breath frequency) 
# based on the last two time units of the session.
@lstm_routes.route("/predict", methods=['POST'])
def predict():
    print("Request on /predict received.")
    request_data = request.json

    required_fields = ['heart_rate_arr', 'binaural_beats_arr', 'visualization_arr', 'breath_multiplier_arr', 'user_id']
    if not all(field in request_data for field in required_fields):
        return jsonify({'error': 'Missing required fields in the request.'}), 400

    heart_rate_arr = request_data['heart_rate_arr']
    binaural_beats_arr = request_data['binaural_beats_arr']
    visualization_arr = request_data['visualization_arr']
    breath_multiplier_arr = request_data['breath_multiplier_arr']
    user_id = request_data['user_id']

    session_data_two_time_units = np.array([heart_rate_arr, binaural_beats_arr, visualization_arr, breath_multiplier_arr])

    prediction = meditation_lstm.predict_next_heart_rate(session_data_two_time_units, user_id)

    if (prediction is None):
        return jsonify({'error': 'User hat noch kein Modell.'}), 400

    return jsonify({'best_combination': {
        'binauralBeatsInHz': prediction[1][0],
        'visualization': int(prediction[2][0]),
        'breathFrequency': prediction[3][0]
    }})


# This route trains the model with the given training data.
@lstm_routes.route("/train_model", methods=['POST'])
def train_model():
    print("Request on /train_model received.")
    request_data = request.json

    required_fields = ['user_id', 'training_data']
    if not all(field in request_data for field in required_fields):
        return jsonify({'error': 'Missing required fields in the request.'}), 400

    training_data_arr = request_data['training_data']

    training_data = np.array(training_data_arr)
    user_id = request_data['user_id']

    meditation_lstm.train_model_with_session_data(training_data, user_id)

    return jsonify({'message': 'Modell für User ' + user_id + ' erfolgreich trainiert.'})
