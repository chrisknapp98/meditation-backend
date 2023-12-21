from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import lstm.meditation_lstm as meditation_lstm

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

    # print length of each array
    print("Length of heart_rate_arr: " + str(len(heart_rate_arr)))
    print("Length of binaural_beats_arr: " + str(len(binaural_beats_arr)))
    print("Length of visualization_arr: " + str(len(visualization_arr)))
    print("Length of breath_multiplier_arr: " + str(len(breath_multiplier_arr)))


    session_data_two_time_units = np.array([heart_rate_arr, binaural_beats_arr, visualization_arr, breath_multiplier_arr])

    prediction = meditation_lstm.predict_next_heart_rate(session_data_two_time_units, user_id)

    return jsonify({'best_combination': {
        'binauralBeatsInHz': prediction[1][0],
        'visualization': int(prediction[2][0]),
        'breathFrequency': prediction[3][0]
    }})

def train_model():
    request_data = request.json

    required_fields = ['user_id', 'training_data']
    if not all(field in request_data for field in required_fields):
        return jsonify({'error': 'Missing required fields in the request.'}), 400

    training_data_arr = request_data['training_data']
    print("Length of training_data_arr: " + str(len(training_data_arr)))

    training_data = np.array(training_data_arr)

    print("Shape of training_data_arr: " + str(np.shape(training_data)))
    user_id = request_data['user_id']

    meditation_lstm.train_model_with_session_data(training_data, user_id)

    return jsonify({'message': 'Modell für User ' + user_id + ' erfolgreich trainiert.'})