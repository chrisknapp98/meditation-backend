import logging
from enum import Enum

from flask import request, jsonify, Blueprint
import numpy as np
import lstm.meditation_lstm as meditation_lstm
from routes.meditation_routes import (validate_meditation_session_data, get_last_session_from_db, save_session_to_db,
                                      get_all_sessions_from_db)

lstm_routes = Blueprint('lstm_routes', __name__)


class Visualization(Enum):
    Arctic = 0
    Aurora = 1
    Circle = 2
    City = 3
    Golden = 4
    Japan = 5
    Metropolis = 6
    Nature = 7
    Plants = 8
    Skyline = 9


@lstm_routes.route("/predict", methods=['POST'])
def predict():
    print(request.json)

    request_data = request.json

    validated_data, error = validate_meditation_session_data(request_data)
    if error:
        error_message, status_code = error
        return jsonify(error_message), status_code

    device_id = validated_data['deviceId']

    # get all meditation sessions for device_id from db
    all_sessions = get_all_sessions_from_db(device_id)
    if len(all_sessions) < 2:
        return jsonify(
            {'message': 'Couldn\'t predict best combination for ' + device_id + '. Not enough data available.'})

    session_periods = []
    if len(validated_data['sessionPeriods']) < 2:
        last_session = get_last_session_from_db(device_id)
        session_periods = last_session.to_dict()['sessionPeriods'][-1:] + validated_data['sessionPeriods']
    else:
        session_periods = validated_data['sessionPeriods'][-2:]

    prediction_formatted_session_periods = map_session_periods_to_prediction_array(session_periods)
    session_data_two_time_units = np.array(prediction_formatted_session_periods)

    prediction = meditation_lstm.predict_next_heart_rate(session_data_two_time_units, device_id)
    if prediction is None:
        return jsonify({'message': f'Could not predict best combination for {device_id}. '
                                   f'User does not have any model yet.'}), 400
    return jsonify({'bestCombination': {
        'beatFrequency': prediction[1][0],
        'visualization': get_visualization_name(int(prediction[2][0])),
        'breathingPatternMultiplier': prediction[3][0]
    }})


# This route trains the model with the given training data.
@lstm_routes.route("/train_model", methods=['POST'])
def train_model():
    device_id: str = request.args.get('deviceId')
    if device_id is None or len(device_id) == 0:
        return jsonify({'error': 'No device id provided.'}), 400
    print(f"Request on /train_model received from device with id: {device_id}")
    previous_sessions = get_all_sessions_from_db(device_id)
    if not previous_sessions:
        return jsonify({'message': f'No previous sessions found for device {device_id}. Could not train model.'})
    previous_sessions.reverse()
    session_periods: list = []
    # Iterate over the reversed previous_sessions and add periods until batch_size is reached
    for session in previous_sessions:
        if len(session_periods) < meditation_lstm.TRAINING_DATA_ARR_SIZE:
            session_periods.extend(session.to_dict()['sessionPeriods'])
        else:
            break
    if len(session_periods) < meditation_lstm.TRAINING_DATA_ARR_SIZE:
        return jsonify(
            {'message': f'Model for device "{device_id}" not trained. Could not find enough previous sessions.'})
    training_data_arr = map_session_periods_to_training_data(session_periods[:meditation_lstm.TRAINING_DATA_ARR_SIZE])
    training_data = np.array(training_data_arr)

    logging.info("Shape of training_data_arr: " + str(np.shape(training_data)))

    meditation_lstm.train_model_with_session_data(training_data, device_id)
    return jsonify({'message': f'Model for device {device_id} trained successfully.'})


def map_session_periods_to_prediction_array(session_periods):
    number_of_heart_rate_entries_per_period = len(session_periods[0]['heartRateMeasurements'])
    heart_rate_arr = []
    binaural_beats_arr = []
    visualization_arr = []
    breath_multiplier_arr = []
    for period in session_periods:
        heart_rate_arr += [hrm['heartRate'] for hrm in period['heartRateMeasurements']]
        binaural_beats_arr += [period['beatFrequency']] * number_of_heart_rate_entries_per_period
        visualization_arr += [get_visualization_number(
            period['visualization'])] * number_of_heart_rate_entries_per_period
        breath_multiplier_arr += [period['breathingPatternMultiplier']] * number_of_heart_rate_entries_per_period

    # print length of each array
    logging.info("Length of heart_rate_arr: " + str(len(heart_rate_arr)))
    logging.info("Length of binaural_beats_arr: " + str(len(binaural_beats_arr)))
    logging.info("Length of visualization_arr: " + str(len(visualization_arr)))
    logging.info("Length of breath_multiplier_arr: " + str(len(breath_multiplier_arr)))

    return [heart_rate_arr, binaural_beats_arr, visualization_arr, breath_multiplier_arr]


def map_session_periods_to_training_data(session_periods: dict):
    """
    Maps session periods to training data.
    :param session_periods: A list of dictionaries representing session periods, where each dictionary
                            contains information about heart rate measurements, beat frequency, visualization,
                            and breathing pattern multiplier.
    :return: A list of lists containing training data. Each inner list represents a period and includes the
              following data for each time point within the period.
    """
    training_data = []
    for period in session_periods:
        heart_rate_data = [hrm['heartRate'] for hrm in period['heartRateMeasurements']]
        beat_frequency_data = [period['beatFrequency']] * len(heart_rate_data)
        visualization_data = [get_visualization_number(period['visualization'])] * len(heart_rate_data)
        multiplier_data = [period['breathingPatternMultiplier']] * len(heart_rate_data)
        training_data.append([heart_rate_data, beat_frequency_data, visualization_data, multiplier_data])
    return training_data


def get_visualization_number(visualization_name: str):
    """
    Convert visualization name to its corresponding number.
    """
    return Visualization[visualization_name.capitalize()].value


def get_visualization_name(visualization_number: int):
    """
    Convert visualization number back to its corresponding name.
    """
    return Visualization(visualization_number).name
