import numpy as np
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import *
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import RootMeanSquaredError
from tensorflow.keras.optimizers import Adam
# WARNING:absl:At this time, the v2.11+ optimizer `tf.keras.optimizers.Adam` runs slowly on M1/M2 Macs, please use the legacy Keras optimizer instead, located at `tf.keras.optimizers.legacy.Adam`.


def _get_sample_training_data(num_samples=10):
    training_data = []

    for _ in range(num_samples):
        heart_rate = np.random.randint(70, 130, size=30)
        sound_in_hz = np.random.randint(30, 41, size=30)
        visualisation_type = np.random.randint(0, 6, size=30)
        breathing_multiplier = np.random.uniform(0.8, 1.6, size=30)

        training_data.append((heart_rate, sound_in_hz, visualisation_type, breathing_multiplier))

    return np.array(training_data)

def load_model(user_id):
    # Load the model
    model = tf.keras.models.load_model('model3/model_checkpoint.h5')
    return model


# Make sure the shape of the training data is (10,4,30)
def train_model_with_session_data(training_data, user_id):
    # Define constants
    BATCH_SIZE = 10
    NUMBER_OF_TIME_SERIES_TYPES = 4
    TIME_SERIES_LENGTH = 30

    # We make the prediction based on 4 different arrays of time series data: hearth_rate, sound_in_hz, visualisation_type, breathing multiplier
    # These arrays represent the current meditation state from the flutter app and are sent to the server
    # One element in an array represents one second of meditation

    # Make sure the input data is equivalent to the time series length
    assert training_data.shape[0] == BATCH_SIZE, "Die Form der Daten entspricht nicht den Erwartungen (10 Datensätze)."
    assert training_data.shape[1] == NUMBER_OF_TIME_SERIES_TYPES, "Die Form der Daten entspricht nicht den Erwartungen (4 Time-Series-Merkmale)."
    assert training_data.shape[2] == TIME_SERIES_LENGTH, "Die Form der Daten entspricht nicht den Erwartungen (30 Zeitschritte)."

    # DEBUG STUFF
    # Print test one session record (with 4 arrays of time series data)
    #print(training_data[0])
    # Print test one session record (with first array of time series data)
    #print(training_data[0][0])
    # Print test one session record (with first array of time series data) and the first element
    #print(training_data[0][0][0])

    # Convert the arrays into the right data format dividing into features and target
    # The features are the 4 arrays of time series data and the target is the next heart rate
    heart_rate_targets = training_data[:, 0, -1]

    # delete the last element of each array
    training_data = training_data[:, :, :-1]
    print("new training data shape: " + str(training_data.shape))

    # Define the training data (test data?)
    X_train = training_data
    y_train = heart_rate_targets

    print("Training input (X_train) shape: " + str(X_train.shape)); 
    print("Training input (X_train): " + str(X_train))
    print("Determined target (y_train) shape: " + str(y_train.shape))
    print("Determined target (y_train): " + str(y_train))

    # Because of deleting the last element of each array to get the target
    model_input_shape_x = TIME_SERIES_LENGTH - 1

    # Define the model
    model1 = Sequential()
    model1.add(InputLayer((4, model_input_shape_x)))
    model1.add(LSTM(64))
    model1.add(Dense(8, 'relu'))
    model1.add(Dense(1, 'linear'))
    model1.summary()

    checkpoint_path = "models/"+ user_id +"/model_checkpoint.h5"

    # Pfad erstellen, wenn er nicht existiert
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)

    # Compile the model
    # TODO: WHY IT DOESNT WORK WITH save_best_only=True???? -> because of validation data! fix it later
    cp_callback = ModelCheckpoint(checkpoint_path)
    model1.compile(optimizer=Adam(learning_rate=0.001), loss=MeanSquaredError(), metrics=[RootMeanSquaredError()])

    model1.fit(X_train, y_train, epochs=100, callbacks=[cp_callback])



training_data = _get_sample_training_data(10);
print("Training data shape: " + str(training_data.shape))
sample_user_id = "745346"

train_model_with_session_data(training_data, sample_user_id)
