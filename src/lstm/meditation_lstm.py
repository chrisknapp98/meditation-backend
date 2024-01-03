import logging
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import *
from keras.models import load_model
from datetime import datetime

DEFAULT_MODEL_FILE_NAME = os.getenv('DEFAULT_MODEL_FILE_NAME', 'model.keras')
MODEL_SAVE_PATH = os.getenv('MODEL_SAVE_PATH', 'models')
ENABLE_LOG_TRAINING_RESULTS = os.getenv('ENABLE_LOG_TRAINING_RESULTS', 'False').lower() == 'true'
logging.basicConfig(level=getattr(logging, os.getenv('LOG_LEVEL', 'DEBUG')))


# from matplotlib import pyplot as plt
# WARNING:absl:At this time, the v2.11+ optimizer `tf.keras.optimizers.Adam` runs slowly on M1/M2 Macs, please use the legacy Keras optimizer instead, located at `tf.keras.optimizers.legacy.Adam`.

# We make the prediction based on 4 different arrays of time series data: hearth_rate, sound_in_hz, visualisation_type, breathing multiplier
# These arrays represent the current meditation state from the flutter app and are sent to the server
# One element in an array represents two seconds of meditation

# Constants

# Returns input data of shape (40x4x15)
def get_sample_session_data(num_time_units=40):
    session_data = []

    for _ in range(num_time_units):
        heart_rate = np.random.randint(60, 81, size=15)
        binaural_beats = np.random.randint(30, 41, size=15)
        visualization = np.random.randint(0, 6, size=15)
        breath_multiplier = np.random.uniform(0.8, 1.6, size=15)

        session_data.append([heart_rate, binaural_beats, visualization, breath_multiplier])

    return np.array(session_data)


# Make sure the length of heart_rate_arr is 30
def _get_next_random_config(heart_rate_arr):
    # Add missing values to fit model architecture (15 heart rate values) with linear interpolation
    additional_values = 15
    interp_indices = np.linspace(0, len(heart_rate_arr) - 1, additional_values)
    interpolated_values = np.interp(interp_indices, np.arange(len(heart_rate_arr)), heart_rate_arr)
    complete_heart_rate_array = interpolated_values.round().astype(int)
    complete_heart_rate_array = complete_heart_rate_array.tolist()

    # create random integer between 0 and 41
    binaural_hz_random = np.random.randint(1, 41)
    # create random integer between 0 and 6
    visualisation_type_random = np.random.randint(0, 6)
    # create random float between 0.8 and 1.6
    breathing_multiplier_choices = np.arange(0.8, 1.7, 0.1)
    breathing_multiplier_random = np.random.choice(breathing_multiplier_choices)

    # complete_heart_rate_array = np.random.randint(70, 90

    config_test = (
        complete_heart_rate_array,
        [binaural_hz_random] * 15,
        [visualisation_type_random] * 15,
        [breathing_multiplier_random] * 15
    )
    return np.array(config_test)


# Create sample training data
# 4 arrays of time series data (heart rate, sound in hz, visualisation type, breathing multiplier)
# 15 values per array
# 40 = 20 time units (2 seconds each) (20 min meditation)
# returns training data with shape (40, 4, 15)


def _load_model(user_id):
    model_path = f"{MODEL_SAVE_PATH}/{user_id}/{DEFAULT_MODEL_FILE_NAME}"
    if os.path.exists(model_path):
        logging.info(f"The model for the user {user_id} already exists.")
        model = load_model(model_path)
        return model
    else:
        logging.info(f"The model for the user {user_id} does not exist.")


# Input: (40 x 4 x 15)
# Output:
# x_train - 455 x 4 x 45
# x_test - 100 x x 4 x 45
# y_train - 455 x 1
# y_test - 100 x 1
def _preprocess_training_data(training_data):
    # Convert the arrays into the right data format dividing into features and target
    # The features are the 4 arrays of time series data and the target is the next heart rate

    # Shape (40 x 4 x 15) -> create training data in the right format preprocssing (flattened)
    # -> flattened shape 4 x 600

    flattened_array = training_data.transpose(1, 0, 2).reshape((4, -1))

    logging.debug(f"flattened array shape: {flattened_array.shape}")
    logging.debug(f"flattened array (herz): {flattened_array[0][:32]}")
    logging.debug(f"flattened array (sound): {flattened_array[1][:32]}")
    logging.debug(f"flattened array (vis): {flattened_array[2][:32]}")
    logging.debug(f"flattened array (breath): {flattened_array[3][:32]}")

    # Create training data in the right format with shape (?x)4x30 (X_train)
    # y_train 1 value (heart rate)
    # Loop trough flattened array and create new arrays with shape (4, 30)
    # result_X_train = np.array([],[])

    x_train = []
    y_train = []
    for i in range(flattened_array.shape[1]):
        # print(flattened_array.shape)
        # print(flattened_array)

        logging.info(f"i: {i}")
        logging.info(flattened_array.shape[1])
        if i + 45 >= flattened_array.shape[1]:
            break

        # hearth rate as target
        x_train_value = flattened_array[:, i:i + 45]
        y_label_value = flattened_array[0, i + 45]

        x_train.append(x_train_value)
        y_train.append(y_label_value)

        logging.debug(f"Iteration: - picking elements for x_train from {i} to {i + 45}; label index {i + 45}\n")
        logging.debug(f"x_train_shape: {x_train_value.shape}")
        logging.debug(f"y_label: {y_label_value}")

    # Convert the list to a numpy array
    x_train = np.array(x_train)
    y_train = np.array(y_train)

    # Current: 55x4x45
    # Convert into output format (? x 3 x 4 x 15)
    # x_train_new_shape = (X_train_temp.shape[0], 3, 4, 15)
    # X_train = X_train_temp.reshape(x_train_new_shape)

    # Extract the test data
    x_test = x_train[-100:]
    y_test = y_train[-100:]

    # TODO Remove the test data from the training data, comment in for great results :D
    x_train = x_train[:-100]
    y_train = y_train[:-100]

    logging.debug(f"Final training input (X_train) shape: {x_train.shape}")
    logging.debug(f"Final training label (y_train) shape: {y_train.shape}")
    logging.debug(f"Final test input (X_test) shape: {x_test.shape}")
    logging.debug(f"Final test label (y_test) shape: {y_test.shape}")

    logging.info("Training and test data successfully created!")
    return x_train, y_train, x_test, y_test


# Make sure the shape of the session_data is (4x 30)
def predict_next_heart_rate(session_data_two_time_units, user_id):
    model = _load_model(user_id)
    if model is None:
        logging.error("User does not have any model yet.")
        return None

    # Make sure the input data is equivalent to the time series length
    assert session_data_two_time_units.shape[
               0] == 4, "The shape of the data does not meet expectations (4 data points)."
    assert session_data_two_time_units.shape[
               1] == 30, "The shape of the data does not meet expectations (30 time-series features)."

    # Annahme: input_arrays_1, input_arrays_2, input_arrays_3 sind deine Arrays

    min_heart_rate = 999  # placeholder for minimum
    count_tried_combinations = 0
    best_combination = None

    heart_rate_arr = session_data_two_time_units[0]
    while count_tried_combinations < 100:

        # print("Herzfrequenz Array: " + str(heart_rate_arr) + "\n")

        next_possible_combination = _get_next_random_config(heart_rate_arr)

        # print shape of two arrays
        # print("Shape of session_data_two_time_units: " + str(session_data_two_time_units.shape))
        # print("Shape of next_possible_combination: " + str(next_possible_combination.shape))

        complete_input_array = np.concatenate((session_data_two_time_units, next_possible_combination), axis=1)

        # print("Hz: " + str(next_possible_combination[1][0]) + " - Vis: " + str(next_possible_combination[2][0]) + " - Breath: " + str(next_possible_combination[3][0]) + "\n")
        # print(str(next_possible_combination) + "\n")
        # Check if the shape is correct (4 x 45) [session data + possible combination]
        assert complete_input_array.shape[
                   0] == 4, "The shape of the combined data does not meet expectations (4 data points)."
        assert complete_input_array.shape[
                   1] == 45, "The shape of the combined data does not meet expectations (45 time-series features)."

        # Add dimension for correct shape (1 x 4 x 45) (batch size x features x time steps)
        complete_input_array = np.expand_dims(complete_input_array, axis=0)
        # print("Shape of complete_input_array: " + str(complete_input_array.shape))

        predicted_heart_rate = model.predict(complete_input_array)

        # print(str(count_tried_combinations+1) + "/" + str(50) + " - Predicted heart rate: " + str(predicted_heart_rate) + " for combination: " + str(next_possible_combination) + "\n")
        print(predicted_heart_rate)

        if predicted_heart_rate < min_heart_rate:
            min_heart_rate = predicted_heart_rate
            best_combination = next_possible_combination

        count_tried_combinations += 1

    # Der beste Satz von Input-Arrays
    logging.info(f"Result - Best Combination: {best_combination}")
    logging.info(f"Result - Minimum Heart Rate: {min_heart_rate}")
    return best_combination


# Make sure the shape of the training data is (40 x 4 x 15)
def train_model_with_session_data(training_data, user_id):
    # Define constants
    BATCH_SIZE = 40
    NUMBER_OF_TIME_SERIES_TYPES = 4
    TIME_SERIES_LENGTH = 15

    # Make sure the input data is equivalent to the time series length
    assert training_data.shape[0] == BATCH_SIZE, "The shape of the data does not meet expectations (40 data points)."
    assert training_data.shape[
               1] == NUMBER_OF_TIME_SERIES_TYPES, "The shape of the data does not meet expectations (4 time-series features)."
    assert training_data.shape[
               2] == TIME_SERIES_LENGTH, "The shape of the data does not meet expectations (15 time steps)."

    # // TODO Validierungen?
    logging.info("Validierung der Trainingsdaten erfolgreich!")

    # Prüfe ob das Modell bereits existiert
    model = _load_model(user_id)
    x_train, y_train, x_test, y_test = _preprocess_training_data(training_data)
    # müsste dann vom shape batch_sizex3x4x15 sein

    # Print all shapes
    logging.info(f"x_train shape: {x_train.shape}")
    logging.info(f"y_train shape: {y_train.shape}")
    logging.info(f"x_test shape: {x_test.shape}")
    logging.info(f"y_test shape: {y_test.shape}")

    if model is None:
        logging.info("User does not have a model yet -> creating a new model")

        # LSTM Model, every data point has shape 3x4x15 (input dimensions)
        # = Input -> 4 x 45 (Keras erwartet 3 Dimensionen inkl. Batch-size)
        model = Sequential()

        model.add(InputLayer(input_shape=(4, 45)))
        model.add(LSTM(64))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(1, activation='linear'))
        model.summary()
        model.compile(loss='mae', optimizer='adam')
        history = model.fit(x_train, y_train, epochs=50, batch_size=32, validation_data=(x_test, y_test), verbose=2,
                            shuffle=False)

        # Erstelle das Verzeichnis, wenn es nicht existiert
        model_directory = f"{MODEL_SAVE_PATH}/{user_id}"
        os.makedirs(model_directory, exist_ok=True)
    else:
        # User has a model -> load it and continue training
        logging.info("User already has a model -> load it and train further")
        history = model.fit(x_train, y_train, epochs=50, batch_size=32, validation_data=(x_test, y_test), verbose=2,
                            shuffle=False)

    # Save the model
    model.save(f"{MODEL_SAVE_PATH}/{user_id}/{DEFAULT_MODEL_FILE_NAME}")
    if ENABLE_LOG_TRAINING_RESULTS:
        # plot_thread = Thread(target=_plot_history, args=(history,))
        # plot_thread.start()
        _plot_history_to_file(history, user_id)


def _plot_history_to_file(history, user_id):
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('Training Progress of the LSTM Model')
    plt.legend()
    # plt.show()
    now = datetime.now()
    time_identifier = now.strftime("%d_%m_%Y_%H_%M_%S")
    Path("training_plots").mkdir(parents=True, exist_ok=True)
    plt.savefig(f'training_plots/{user_id}__{time_identifier}_plots.png')
