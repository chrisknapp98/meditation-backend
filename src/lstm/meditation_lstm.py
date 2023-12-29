import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import *
from keras.models import load_model
from datetime import datetime

# Define constants
DEFAULT_MODEL_FILE_NAME = os.getenv('DEFAULT_MODEL_FILE_NAME', 'model.keras')
MODEL_SAVE_PATH = os.getenv('MODEL_SAVE_PATH', 'models')
ENABLE_LOG_TRAINING_RESULTS = os.getenv('ENABLE_LOG_TRAINING_RESULTS', 'False').lower() == 'true'
logging.basicConfig(level=getattr(logging, os.getenv('LOG_LEVEL', 'DEBUG')))


# Predict the next heart rate for a given user based on the last two time units of the session.
def predict_next_heart_rate(session_data_two_time_units, user_id):
    model = _load_model(user_id)
    if (model is None):
        print("Fehler. User hat noch garkein Modell.")
        return None

    assert session_data_two_time_units.shape[0] == 4, "Die Form der Daten entspricht nicht den Erwartungen (4 Datensätze)."
    assert session_data_two_time_units.shape[1] == 30, "Die Form der Daten entspricht nicht den Erwartungen (30 Time-Series-Merkmale)."

    min_heart_rate = 999 # placeholder for mimumum
    count_tried_combinations = 0
    best_combination = None

    heart_rate_arr = session_data_two_time_units[0]
    while count_tried_combinations < 100:

        next_possible_combination = _get_next_random_config(heart_rate_arr)
        complete_input_array = np.concatenate((session_data_two_time_units, next_possible_combination), axis=1)

        assert complete_input_array.shape[0] == 4, "Die Form der kombinierten Daten entspricht nicht den Erwartungen (4 Datensätze)."
        assert complete_input_array.shape[1] == 45, "Die Form der kombinierten Daten entspricht nicht den Erwartungen (45 Time-Series-Merkmale)."

        # Add dimension for correct shape (1 x 4 x 45) (batch size x features x time steps)
        complete_input_array = np.expand_dims(complete_input_array, axis=0)

        predicted_heart_rate = model.predict(complete_input_array)

        if predicted_heart_rate < min_heart_rate:
            min_heart_rate = predicted_heart_rate
            best_combination = next_possible_combination

        count_tried_combinations += 1

    print("Ergebnis - Beste Kombination:" + str(best_combination))
    print("Ergebnis - Minimale Herzfrequenz:" + str(min_heart_rate))

    return best_combination


# Train the model with the given training data and user_id.
# Make sure the shape of the training data is (40 x 4 x 15)
def train_model_with_session_data(training_data, user_id):

    BATCH_SIZE = 40
    NUMBER_OF_TIME_SERIES_TYPES = 4
    TIME_SERIES_LENGTH = 15

    assert training_data.shape[0] == BATCH_SIZE, "Die Form der Daten entspricht nicht den Erwartungen (40 Datensätze)."
    assert training_data.shape[1] == NUMBER_OF_TIME_SERIES_TYPES, "Die Form der Daten entspricht nicht den Erwartungen (4 Time-Series-Merkmale)."
    assert training_data.shape[2] == TIME_SERIES_LENGTH, "Die Form der Daten entspricht nicht den Erwartungen (15 Zeitschritte)."
    
    model = _load_model(user_id)
    X_train, y_train, X_test, y_test = _preprocess_training_data(training_data)

    if (ENABLE_LOG_TRAINING_RESULTS):
        print("Validierung der Trainingsdaten erfolgreich!")
        print("X_train shape: " + str(X_train.shape))
        print("y_train shape: " + str(y_train.shape))
        print("X_test shape: " + str(X_test.shape))
        print("y_test shape: " + str(y_test.shape))

    if (model is None):
        print("User hat noch kein Modell -> erstelle ein neues Modell")

        model = Sequential()
        model.add(InputLayer(input_shape=(4, 45)))
        model.add(LSTM(64))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(1, activation='linear'))
        model.summary()
        model.compile(loss='mae', optimizer='adam')
        history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), verbose=2, shuffle=False)

        model_directory = "models/" + user_id
        os.makedirs(model_directory, exist_ok=True)
    else:
        print("User hat bereits ein Modell -> lade es und trainiere nach")
        history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), verbose=2, shuffle=False)

    model.save("models/" + user_id + "/" + DEFAULT_MODEL_FILE_NAME)

    if (ENABLE_LOG_TRAINING_RESULTS):
        _plot_history_to_file(history, user_id)


# Get random session configuration for the next time unit.
def _get_next_random_config(heart_rate_arr):
    # Add missing values to fit model architecture (15 heart rate values) with linear interpolation
    additional_values = 15
    interp_indices = np.linspace(0, len(heart_rate_arr) - 1, additional_values)
    interpolated_values = np.interp(interp_indices, np.arange(len(heart_rate_arr)), heart_rate_arr)
    complete_heart_rate_array = interpolated_values.round().astype(int)
    complete_heart_rate_array = complete_heart_rate_array.tolist()

    binaural_hz_random = np.random.randint(1, 41)
    visualisation_type_random = np.random.randint(0, 6)
    breathing_multiplier_choices = np.arange(0.8, 1.7, 0.1)
    breathing_multiplier_random = np.random.choice(breathing_multiplier_choices)    
                    
    config_test = (
        complete_heart_rate_array,
        [binaural_hz_random] * 15,
        [visualisation_type_random] * 15,
        [breathing_multiplier_random] * 15
    )
    return np.array(config_test)


def _load_model(user_id):
    model_path = f"{MODEL_SAVE_PATH}/{user_id}/{DEFAULT_MODEL_FILE_NAME}"
    if os.path.exists(model_path):
        logging.info(f"The model for the user {user_id} already exists.")
        model = load_model(model_path)
        return model
    else:
        print("Das Modell für den User " + user_id + " existiert nicht.")
        return None


# Preprocess the training data into the right format for the LSTM model using the sliding window approach
# Shapes:
# Input: training_data = (40 x 4 x 15)
# Output: x_train = 455 x 4 x 45 // x_test = 100 x 4 x 45 // y_train = 455 x 1 // y_test = 100 x 1
def _preprocess_training_data(training_data):
    # Convert the arrays into the right data format dividing into features and target
    # The features are the 4 arrays of time series data and the target is the next heart rate
    flattened_array = training_data.transpose(1, 0, 2).reshape((4, -1))

    logging.debug(f"flattened array shape: {flattened_array.shape}")
    logging.debug(f"flattened array (herz): {flattened_array[0][:32]}")
    logging.debug(f"flattened array (sound): {flattened_array[1][:32]}")
    logging.debug(f"flattened array (vis): {flattened_array[2][:32]}")
    logging.debug(f"flattened array (breath): {flattened_array[3][:32]}")

    # Create training data in the right format with shape 455x4x45 (X_train)
    # Loop trough flattened array and create new arrays with shape (4, 30)
    X_train = []
    y_train = []
    for i in range(flattened_array.shape[1]):
        # print(flattened_array.shape)
        # print(flattened_array)

        print("i: " + str(i))
        print(flattened_array.shape[1])
        if (i+45 >= flattened_array.shape[1]):
            print("break")
            break

        # hearth rate as target
        x_train_value = flattened_array[:, i:i + 45]
        y_label_value = flattened_array[0, i + 45]

        X_train.append(x_train_value)
        y_train.append(y_label_value)

        if (ENABLE_LOG_TRAINING_RESULTS):
            print("Durchlauf: - picke für X_train Elemente von " + str(i) + " bis " + str(i+45) + "; label index " + str(i+45) + "\n")
            print("x_train_shape: " + str(x_train_value.shape))
            print("y_label: " + str(y_label_value))

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    X_test = X_train[-100:]
    y_test = y_train[-100:]

    # Remove the test data from the training data, (comment out for great results :D)
    X_train = X_train[:-100]
    y_train = y_train[:-100]

    logging.debug(f"Final training input (X_train) shape: {X_train.shape}")
    logging.debug(f"Final training label (y_train) shape: {y_train.shape}")
    logging.debug(f"Final test input (X_test) shape: {X_test.shape}")
    logging.debug(f"Final test label (y_test) shape: {y_test.shape}")

    logging.info("Training and test data successfully created!")
    return X_train, y_train, X_test, y_test


# Plot the training history for a user and save the png to a file
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
    plt.savefig('training_plots/'+ str(user_id) + "__" + str(time_identifier) + '_plots.png')


# Used for development only to create sample training data.
# Returns 4 arrays of time series data (heart rate, sound in hz, visualisation type, breathing multiplier) with shape (40, 4, 15)
def _test_get_sample_session_data(num_time_units=40):
    session_data = []

    for _ in range(num_time_units):
        heart_rate = np.random.randint(60, 81, size=15)
        binaural_beats = np.random.randint(30, 41, size=15)
        visualization = np.random.randint(0, 6, size=15)
        breath_multiplier = np.random.uniform(0.8, 1.6, size=15)

        session_data.append([heart_rate, binaural_beats, visualization, breath_multiplier])

    return np.array(session_data)
