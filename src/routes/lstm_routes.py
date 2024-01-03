from flask import request, jsonify, Blueprint
import numpy as np
import lstm.meditation_lstm as meditation_lstm
from routes.meditation_routes import validate_meditation_session_data, get_last_session_from_db, remove_session_from_db, save_session_to_db, get_all_sessions_from_db

lstm_routes = Blueprint('lstm_routes', __name__)


@lstm_routes.route("/predict", methods=['POST'])
def predict():
    request_data = request.json
    
    validated_data, error = validate_meditation_session_data(request_data)
    if error:
        error_message, status_code = error
        return jsonify(error_message), status_code

    device_id = validated_data['deviceId']

    # get all meditation sessions for device_id from db
    all_sessions = get_all_sessions_from_db(device_id)
    if len(all_sessions) < 2:
        return jsonify({'message': 'Couldn\'t predict best combination for ' + device_id + '. Not enough data available.'})

    session_periods = []    
    if len(validated_data['sessionPeriods']) < 2:
        last_session = get_last_session_from_db(device_id)
        session_periods = last_session.to_dict()['sessionPeriods'][-1:] + validated_data['sessionPeriods']
    else:
        session_periods = validated_data['sessionPeriods'][-2:]

    prediction_formatted_session_periods = map_session_periods_to_prediction_array(session_periods)
    session_data_two_time_units = np.array(prediction_formatted_session_periods)

    prediction = meditation_lstm.predict_next_heart_rate(session_data_two_time_units, device_id)
    
    # Debugging: print the predicted visualization number
    print("Predicted visualization number:", prediction[2][0])

    return jsonify({'bestCombination': {
        'beatFrequency': prediction[1][0],
        'visualization': get_visualization_name(int(prediction[2][0])),
        'breathingPatternMultiplier': prediction[3][0]
    }})


@lstm_routes.route("/train_model", methods=['POST'])
def train_model():
    request_data = request.json

    validated_data, error = validate_meditation_session_data(request_data)
    if error:
        error_message, status_code = error
        return jsonify(error_message), status_code
    
    training_data_arr = []

    if validated_data['isCompleted']:
        previous_sessions = get_all_sessions_from_db(validated_data['deviceId'])
        save_session_to_db(validated_data)

        if not previous_sessions:
            return jsonify({'message': 'Session saved, but Model for device ' + validated_data['deviceId'] + ' was not trained as no previous session was found.'})

        combined_session_periods = validated_data['sessionPeriods'].copy()
        previous_sessions.reverse()
        # Iterate over the reversed previous_sessions and add periods until batch_size is reached
        for session in previous_sessions:
            if len(combined_session_periods) < training_data_arr_size:
                additional_periods_needed = training_data_arr_size - len(combined_session_periods)
                session_periods = session.to_dict()['sessionPeriods']
                # Take only as many periods as needed from this session
                combined_session_periods.extend(session_periods[:additional_periods_needed])
            else:
                break

        training_data_arr = map_session_periods_to_training_data(combined_session_periods)
        print("Length of training_data_arr: " + str(len(training_data_arr)))
    else: 
        return jsonify({'message': 'Model for device ' + validated_data['deviceId'] + ' not trained. Session did not complete.'})

    training_data = np.array(training_data_arr)

    print("Shape of training_data_arr: " + str(np.shape(training_data)))
    device_id = validated_data['deviceId']

    meditation_lstm.train_model_with_session_data(training_data, device_id)

    return jsonify({'message': 'Model for device ' + device_id + ' trained successfully.'})


def map_session_periods_to_prediction_array(session_periods):
    number_of_heart_rate_entries_per_period = len(session_periods[0]['heartRateMeasurements'])
    heart_rate_arr = []
    binaural_beats_arr = []
    visualization_arr = []
    breath_multiplier_arr = []
    for period in session_periods:
        heart_rate_arr += [hrm['heartRate'] for hrm in period['heartRateMeasurements']]
        binaural_beats_arr += [period['beatFrequency']] * number_of_heart_rate_entries_per_period
        visualization_arr += [get_visualization_number(period['visualization'])] * number_of_heart_rate_entries_per_period
        breath_multiplier_arr += [period['breathingPatternMultiplier']] * number_of_heart_rate_entries_per_period

    # print length of each array
    print("Length of heart_rate_arr: " + str(len(heart_rate_arr)))
    print("Length of binaural_beats_arr: " + str(len(binaural_beats_arr)))
    print("Length of visualization_arr: " + str(len(visualization_arr)))
    print("Length of breath_multiplier_arr: " + str(len(breath_multiplier_arr)))

    return [heart_rate_arr, binaural_beats_arr, visualization_arr, breath_multiplier_arr]

def map_session_periods_to_training_data(session_periods):
    training_data = []
    for period in session_periods:
        heart_rate_data = [hrm['heartRate'] for hrm in period['heartRateMeasurements']]
        beat_frequency_data = [period['beatFrequency']] * len(heart_rate_data)
        visualization_data = [get_visualization_number(period['visualization'])] * len(heart_rate_data)
        multiplier_data = [period['breathingPatternMultiplier']] * len(heart_rate_data)
        training_data.append([heart_rate_data, beat_frequency_data, visualization_data, multiplier_data])
    return training_data

# List of tuples for visualization mapping
visualization_list = [
    ('Arctic', 0),
    ('Aurora', 1),
    ('Circle', 2),
    ('City', 3),
    ('Golden', 4),
    ('Japan', 5),
    ('Metropolis', 6),
    ('Nature', 7),
    ('Plants', 8),
    ('Skyline', 9),
]

# Convert to dictionaries for easy lookup
visualization_mapping_str_to_num = dict(visualization_list)
visualization_mapping_num_to_str = {num: name for name, num in visualization_list}

def get_visualization_number(visualization_name):
    """Convert visualization name to its corresponding number."""
    return visualization_mapping_str_to_num.get(visualization_name, 0)

def get_visualization_name(visualization_number):
    """Convert visualization number back to its corresponding name."""
    return visualization_mapping_num_to_str.get(visualization_number)

training_data_arr_size = 40