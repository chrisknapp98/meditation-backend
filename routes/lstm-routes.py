from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import lstm.meditation_lstm as meditation_lstm

def test(request):
        # Test stuff
    MAKE_PREDICTION = True
    sample_user_id = "456"

    if (MAKE_PREDICTION):

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


        print(session_data_two_time_units_1.shape)

        # Array umformen zu (1, 4, 30)
        reshaped_array = session_data_two_time_units_1[np.newaxis, :, :]
        # Das Array in die Form (4, 30) umformen
        #reshaped_array = session_data_two_time_units_1.reshape(4, 30)
        #reshaped_array = session_data_two_time_units_1[np.newaxis, :, :]

        #print(reshaped_array)


        print(reshaped_array.shape)
        # Vorhersage
        prediction = meditation_lstm.predict_next_heart_rate(reshaped_array, sample_user_id)

        print("hearth rate: " + str(prediction));
        return jsonify({'message': 'Hello World!'})
    else:
        # Create sample training data for one meditation session (40 time units)
        training_data = meditation_lstm._get_sample_training_data(num_time_units=40)
        training_data = np.array(training_data)



        print("Training data shape: " + str(training_data.shape))
        #print(str(training_data))

        meditation_lstm.train_model_with_session_data(training_data, sample_user_id)
        return jsonify({'message': 'Hello World!'})
    

def predict(request):
    # Preprocessing missing values
    # Länge der 4 Datenarrays -> 30 Werte pro Array
    # Validierung der Werte der 4 Datenarrays -> 60-120, 30-40, 0-5, 0.8-1.6 (?)
    # Ggf. fehlende Werte einfügen


    # Parse JSON data from the request body
    data = request.json

    # Your model prediction logic here
    result = {"prediction": "some_result"}

    # Return the result as JSON
    return jsonify(result)

def train_model(request):
    print("hello")