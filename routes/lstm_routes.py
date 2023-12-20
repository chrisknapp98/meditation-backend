from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import lstm.meditation_lstm as meditation_lstm


   

def predict():
    # Preprocessing missing values
    # Länge der 4 Datenarrays -> 30 Werte pro Array
    # Validierung der Werte der 4 Datenarrays -> 60-120, 30-40, 0-5, 0.8-1.6 (?)
    # Ggf. fehlende Werte einfügen

    # Beispiel prediction data
    first_row = [60, 65, 70, 75, 80, 60, 65, 70, 75, 80, 60, 65, 70, 75, 80, 60, 65, 70, 75, 80, 60, 65, 70, 75, 80, 60, 65, 70, 75, 80]
    second_row = [30] * 15 + [32] * 15
    third_row = [1] * 15 + [3] * 15
    fourth_row = [1.2] * 15 + [0.8] * 15

    # Gesamter Array
    session_data_two_time_units_1 = np.array([
            first_row,
            second_row,
            third_row,
            fourth_row
    ])
    sample_user_id = "123"

    # TODO get data from request object

    print(session_data_two_time_units_1.shape)

    prediction = meditation_lstm.predict_next_heart_rate(session_data_two_time_units_1, sample_user_id)

    print("hearth rate: " + str(prediction))

    return jsonify({'best_combination': {
        'binauralBeatsInHz': prediction[1][0],
        'visualization': int(prediction[2][0]),
        'breathFrequency': prediction[3][0]
    }})
    

def train_model():
    # Create sample training data for one meditation session (40 time units)
    training_data = meditation_lstm._get_sample_training_data(num_time_units=40)
    sample_user_id = "123"
    # TODO get data from request object

    training_data = np.array(training_data)
    print("Training data shape: " + str(training_data.shape))

    meditation_lstm.train_model_with_session_data(training_data, sample_user_id)
    return jsonify({'message': 'Modell für User ' + sample_user_id + ' trainiert.'})