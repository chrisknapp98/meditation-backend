import numpy as np
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import *
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import RootMeanSquaredError
from tensorflow.keras.optimizers import Adam
from keras.models import load_model
import app_config as app_config
import itertools

from matplotlib import pyplot
# WARNING:absl:At this time, the v2.11+ optimizer `tf.keras.optimizers.Adam` runs slowly on M1/M2 Macs, please use the legacy Keras optimizer instead, located at `tf.keras.optimizers.legacy.Adam`.

# We make the prediction based on 4 different arrays of time series data: hearth_rate, sound_in_hz, visualisation_type, breathing multiplier
# These arrays represent the current meditation state from the flutter app and are sent to the server
# One element in an array represents two seconds of meditation

# Constants

# Returns input data of shape (1x4x30)
def get_sample_session_data():
    first_row = [60, 65, 70, 75, 80, 60, 65, 70, 75, 80, 60, 65, 70, 75, 80, 60, 65, 70, 75, 80, 60, 65, 70, 75, 80, 60, 65, 70, 75, 80]
    second_row = [30] * 15 + [32] * 15
    third_row = [1] * 15 + [3] * 15
    fourth_row = [1.2] * 15 + [0.8] * 15

    session_data_two_time_units_1 = np.array([
        first_row,
        second_row,
        third_row,
        fourth_row
    ])

    # Array umformen zu (1, 4, 30)
    reshaped_array = session_data_two_time_units_1[np.newaxis, :, :]
    return reshaped_array

def _get_next_random_config():
    config_test = (
        np.random.randint(70, 130, size=15),
        np.random.randint(30, 41, size=15),
        np.random.randint(0, 6, size=15),
        np.random.uniform(0.8, 1.6, size=15)
    )
    return np.expand_dims(np.stack(config_test, axis=-1), axis=0).transpose((0, 2, 1))

# Create sample training data
# 4 arrays of time series data (heart rate, sound in hz, visualisation type, breathing multiplier)
# 2 time units + 1 config to test
# 15 values per array
# returns training data with shape (20, 4, 15)
def _get_sample_training_data(num_time_units=20):
    training_data = []

    # Create two sample data session arrays
    for _ in range(num_time_units):
        heart_rate = np.random.randint(60, 110, size=15)
        sound_in_hz = np.random.randint(30, 41, size=15)
        visualisation_type = np.random.randint(0, 6, size=15)
        breathing_multiplier = np.random.uniform(0.8, 1.6, size=15)

        training_data.append((heart_rate, sound_in_hz, visualisation_type, breathing_multiplier))

    return np.array(training_data)

def _load_model(user_id):
    model_path = "models/" + user_id + "/" + app_config.DEFAULT_MODEL_FILE_NAME
    if (os.path.exists(model_path)):
        print("Das Modell für den User " + user_id + " existiert bereits.")
        model = load_model(model_path)
        return model
    else:
        print("Das Modell für den User " + user_id + " existiert nicht.")
        return None
    
def _preprocess_training_data(training_data):

    # Convert the arrays into the right data format dividing into features and target
    # The features are the 4 arrays of time series data and the target is the next heart rate
    
    # Shape (20 x 4 x 15) -> create training data in the right format preprocssing (flattened)
    # -> flattened shape 4 x 600

    flattened_array = training_data.transpose(1, 0, 2).reshape((4, -1))
    
    if (app_config.ENABLE_DETAILED_LOGGING):
        print("flattened array shape: " + str(flattened_array.shape))
        print("flattened array (herz): " + str(flattened_array[0][:32]))
        print("flattened array (sound): " + str(flattened_array[1][:32]))
        print("flattened array(vis): " + str(flattened_array[2][:32]))
        print("flattened array (breath): " + str(flattened_array[3][:32]))
        print("------")



    # Create training data in the right format with shape (?x)4x30 (X_train)
    # y_train 1 value (heart rate)
    # Loop trough flattened array and create new arrays with shape (4, 30)
    #result_X_train = np.array([],[])

    X_train = []
    y_train = []
    for i in range(0, flattened_array.shape[1]):

        #print(flattened_array.shape)
        #print(flattened_array)

        print("i: " + str(i))
        print(flattened_array.shape[1])
        if (i+30 >= flattened_array.shape[1]):
            print("break")
            break
        
        # hearth rate as target
        x_train_value = flattened_array[:, i:i+30]
        y_label_value = flattened_array[0, i+30]
        
        X_train.append(x_train_value)
        y_train.append(y_label_value)

        if (app_config.ENABLE_DETAILED_LOGGING):
            print("Durchlauf: - picke für X_train Elemente von " + str(i) + " bis " + str(i+30) + "; label index " + str(i+30) + "\n")
            print("x_train_shape: " + str(x_train_value.shape))
            print("y_label: " + str(y_label_value))


    # Convert the list to a numpy array
    X_train = np.array(X_train)
    y_train = np.array(y_train)

    if (app_config.ENABLE_DETAILED_LOGGING):
        print("Training input (X_train) shape: " + str(X_train.shape)); 
        print("Training label (y_train) shape: " + str(y_train.shape))

    # Extract the test data
    X_test = X_train[-100:]
    y_test = y_train[-100:]

    print("Trainings und Testdaten erfolgreich erstellt!")

    return X_train, y_train, X_test, y_test


def _plot_training_history(history):
    pyplot.plot(history.history['loss'], label='Training Loss')
    pyplot.plot(history.history['val_loss'], label='Validation Loss')
    pyplot.xlabel('Epochen')
    pyplot.ylabel('Loss')
    pyplot.title('Trainingsverlauf des LSTM-Modells')
    pyplot.legend()
    pyplot.show()

# Make sure the shape of the session_data is (1 x 4 x 30)
def predict_next_heart_rate(session_data_two_time_units, user_id):
    model = _load_model(user_id)
    if (model is None):
        print("Fehler. User hat noch garkein Modell.")
        return None

    # Make sure the input data is equivalent to the time series length
    assert session_data_two_time_units.shape[0] == 1, "Die Form der Daten entspricht nicht den Erwartungen (1 Datensätze)."
    assert session_data_two_time_units.shape[1] == 4, "Die Form der Daten entspricht nicht den Erwartungen (4 Datensätze)."
    assert session_data_two_time_units.shape[2] == 30, "Die Form der Daten entspricht nicht den Erwartungen (30 Time-Series-Merkmale)."

    # 
    # Annahme: input_arrays_1, input_arrays_2, input_arrays_3 sind deine Arrays

    min_heart_rate = 999 # placeholder for mimumum
    count_tried_combinations = 0
    while count_tried_combinations < 50:

        next_possible_combination = _get_next_random_config()

        # print shape of two arrays
        print("Shape of session_data_two_time_units: " + str(session_data_two_time_units.shape))
        print("Shape of next_possible_combination: " + str(next_possible_combination.shape))

        complete_input_array = np.concatenate((session_data_two_time_units, next_possible_combination), axis=2)

        # Check if the shape is correct (1 x 4 x 45) [session data + possible combination]
        assert complete_input_array.shape[0] == 1, "Die Form der kombinierten Daten entspricht nicht den Erwartungen (1 Datensätze)."
        assert complete_input_array.shape[1] == 4, "Die Form der kombinierten Daten entspricht nicht den Erwartungen (4 Datensätze)."
        assert complete_input_array.shape[2] == 45, "Die Form der kombinierten Daten entspricht nicht den Erwartungen (45 Time-Series-Merkmale)."

        prediction = model.predict(complete_input_array)

        prediction = model.predict(session_data_two_time_units)
        return prediction
        exit()
        # Placeholder für das Minimum
        best_combination = None

        # Durchlaufe alle Kombinationen
        for combination in all_combinations:
            # Hier führst du dein Modelltraining und die Vorhersagen durch
            # Implementiere die Logik, um die Herzfrequenz zu erhalten
            heart_rate = train_and_predict(combination)

            # Wenn die aktuelle Kombination eine niedrigere Herzfrequenz hat, aktualisiere das Minimum
            if heart_rate < min_heart_rate:
                min_heart_rate = heart_rate
                best_combination = combination

        # Der beste Satz von Input-Arrays
        print("Beste Kombination:", best_combination)
        print("Minimale Herzfrequenz:", min_heart_rate)

        # Make prediction
        prediction = model.predict(session_data_two_time_units)
        print("Prediction für User " + user_id + " - " + str(prediction) + " (heart rate))")

    return prediction

# Make sure the shape of the training data is (40 x 4 x 15)
def train_model_with_session_data(training_data, user_id):

    # Define constants
    BATCH_SIZE = 40
    NUMBER_OF_TIME_SERIES_TYPES = 4
    TIME_SERIES_LENGTH = 15

    # Make sure the input data is equivalent to the time series length
    assert training_data.shape[0] == BATCH_SIZE, "Die Form der Daten entspricht nicht den Erwartungen (40 Datensätze)."
    assert training_data.shape[1] == NUMBER_OF_TIME_SERIES_TYPES, "Die Form der Daten entspricht nicht den Erwartungen (4 Time-Series-Merkmale)."
    assert training_data.shape[2] == TIME_SERIES_LENGTH, "Die Form der Daten entspricht nicht den Erwartungen (15 Zeitschritte)."

    # // TODO Validierungen?

    print("Validierung der Trainingsdaten erfolgreich!")

    # Prüfe ob das Modell bereits existiert
    model = _load_model(user_id)
    X_train, y_train, X_test, y_test = _preprocess_training_data(training_data)
    # müsste dann vom shape batch_sizex3x4x15 sein

    # Print all shapes
    print("X_train shape: " + str(X_train.shape))
    print("y_train shape: " + str(y_train.shape))
    print("X_test shape: " + str(X_test.shape))
    print("y_test shape: " + str(y_test.shape))

    if (model is None):
        # User has no model yet -> create a new one
        print("User hat noch kein Modell -> erstelle ein neues Modell")

        # LSTM Model, every data point has shape 3x4x15 (input dimensions)
        model = Sequential()

        model.add(InputLayer(input_shape=(3, 4, 15)))
        model.add(LSTM(64))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(1, activation='linear'))
        model.summary()
        model.compile(loss='mae', optimizer='adam')
        # TODO Batch size anpassen
        history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), verbose=2, shuffle=False)

        # Erstelle das Verzeichnis, wenn es nicht existiert
        model_directory = "models/" + user_id
        os.makedirs(model_directory, exist_ok=True)
    else:
        # User has a model -> load it and continue training
        print("User hat bereits ein Modell -> lade es und trainiere nach")
        history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), verbose=2, shuffle=False)

    # Save the model
    model.save("models/" + user_id + "/" + app_config.DEFAULT_MODEL_FILE_NAME)

    if (app_config.ENABLE_LOG_TRAINING_RESULTS):
        _plot_training_history(history)


