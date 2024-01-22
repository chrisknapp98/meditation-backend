
*** Variables ***

${BACKEND_URL}  http://localhost:6000
${DEVICE_ID}  RANDOMLY_GENERATED
${TRAIN_MODEL_PAYLOAD}  DEFINE_IN_VARIABLES_FILE
${PREDICT_PAYLOAD}  DEFINE_IN_VARIABLES_FILE
${MEDITAIONS_URI}  /meditations
${TRAIN_MODEL_URI}  /train_model
${PREDICT_URI}  /predict
&{DEVICE_ID_DICT}  deviceId=${DEVICE_ID}

${NO_MEDITAIONS_FOUND_TEXT}  No meditation sessions found
${MEDITAION_SESSION_CREATED_TEXT}  Meditation session created successfully
${MODEL_TRAINED_TEXT}  Model for device {device_id} trained successfully.
${COULD_NOT_TRAIN_MODEL}  Model for device "{device_id}" not trained. Could not find enough previous sessions.
${NO_PREVIOUS_SESSION_FOUND}  No previous sessions found for device {device_id}. Could not train model.
${NOT_ENOUGH_DATA_TEXT}  Couldn't predict best combination for {device_id}. Not enough data available.

*** Settings ***
Documentation  This test suite is designed to validate the functionality of a backend service related to a meditation
...            application.
Library    RequestsLibrary
Library    String
Library    Collections

Suite Setup    Create Session  meditation-backend  ${BACKEND_URL}

*** Test Cases ***
Generate UUID
    [Documentation]  Generates a random UUID and sets it as value for all payloads.
    ${DEVICE_ID}=    Generate UUID
    Log    Generated UUID: ${DEVICE_ID}
    Set Suite Variable  ${DEVICE_ID}
    ${TRAIN_MODEL_PAYLOAD}=  Set To Dictionary    ${TRAIN_MODEL_PAYLOAD}  deviceId=${DEVICE_ID}
    ${PREDICT_PAYLOAD}=  Set To Dictionary    ${PREDICT_PAYLOAD}  deviceId=${DEVICE_ID}
    Set To Dictionary    ${DEVICE_ID_DICT}  deviceId=${DEVICE_ID}

Get All Sessions By Device Id No Sessions Created
    [Documentation]  Get all sessions for a device id which has no data stored yet.
    ${response}=    GET On Session  meditation-backend  ${MEDITAIONS_URI}  params=${DEVICE_ID_DICT}
    ...                             expected_status=404
    Should Be Equal  ${NO_MEDITAIONS_FOUND_TEXT}  ${response.json()}[message]

Predict Before Sessions Stored
    [Documentation]  Tries to get a prediction before the model was trained. Should fail, because there is not enough
    ...              data yet to make predictions.
    ${response}=    Post On Session  meditation-backend  ${PREDICT_URI}  json=${PREDICT_PAYLOAD}
    ...                              expected_status=200
    ${EXPECTED_MESSAGE}=  Format String  ${NOT_ENOUGH_DATA_TEXT}  device_id=${DEVICE_ID}
    Should Be Equal  ${EXPECTED_MESSAGE}  ${response.json()}[message]

Train Model No Previous Session
    [Documentation]  Sends the first chunk of training data. The backend should respond, that no previous data was found.
    ${response}=    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  params=${DEVICE_ID_DICT}
    ...                             expected_status=200
    ${EXPECTED_MESSAGE}=  Format String  ${NO_PREVIOUS_SESSION_FOUND}  device_id=${DEVICE_ID}
    Should Be Equal  ${EXPECTED_MESSAGE}  ${response.json()}[message]

Store Sessions
    [Documentation]  Send the first chunk of training data
    ${response}=    Post On Session  meditation-backend  ${MEDITAIONS_URI}  json=${TRAIN_MODEL_PAYLOAD}
    ...                             expected_status=201
    Should Be Equal  ${MEDITAION_SESSION_CREATED_TEXT}  ${response.json()}[message]

Train Model Not Enough Data
    [Documentation]  Send request to train the model. The server should respond that there are not enough training data
    ...              available yet.
    ${response}=    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  params=${DEVICE_ID_DICT}
    ...                             expected_status=200
    ${EXPECTED_MESSAGE}=  Format String  ${COULD_NOT_TRAIN_MODEL}  device_id=${DEVICE_ID}
    Should Be Equal  ${EXPECTED_MESSAGE}  ${response.json()}[message]

Store Sessions Again
    [Documentation]  Send the second chunk of training data to make sure that the model can be trained.
    ${response}=    Post On Session  meditation-backend  ${MEDITAIONS_URI}  json=${TRAIN_MODEL_PAYLOAD}
    ...                             expected_status=201
    Should Be Equal  ${MEDITAION_SESSION_CREATED_TEXT}  ${response.json()}[message]

Train Model
    [Documentation]  Send request to train the model. The server should respond that there are not enough training data
    ...              available yet.
    ${response}=    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  params=${DEVICE_ID_DICT}
    ...                             expected_status=200
    ${EXPECTED_MESSAGE}=  Format String  ${MODEL_TRAINED_TEXT}  device_id=${DEVICE_ID}
    Should Be Equal  ${EXPECTED_MESSAGE}  ${response.json()}[message]

Train Model Empty Device Id
    [Documentation]  Sends a training payload with an empty device id. The server should respond with an error.
    ${EMPTY_DEVICE_ID_DICT}=  Copy Dictionary  ${DEVICE_ID_DICT}  deep_copy=${True}
    ${EMPTY_DEVICE_ID_DICT}[deviceId]=  Set Variable    ${EMPTY}
    ${response}=    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  params=${EMPTY_DEVICE_ID_DICT}
    ...                             expected_status=400

Predict After Training
    [Documentation]  Sends a request to get a prediction after the model has been trained with sufficient data.
    ...              Additionally, validates whether all expected keys are present in the response JSON.
    ${response}=    Post On Session  meditation-backend  ${PREDICT_URI}  json=${PREDICT_PAYLOAD}
    ...                              expected_status=200
    ${recommended_parameters}=  Set Variable  ${response.json()}[bestCombination]

    Dictionary Should Contain Key  ${recommended_parameters}  beatFrequency
    Dictionary Should Contain Key  ${recommended_parameters}  breathingPatternMultiplier
    Dictionary Should Contain Key  ${recommended_parameters}  visualization

Predict Empty Device Id
    [Documentation]    Sends a prediction payload with an empty device id. The server should respond with an error.
    ${PREDICT_PAYLOAD_EMPTY_DEVICE_ID}=  Copy Dictionary  ${PREDICT_PAYLOAD}  deep_copy=${True}
    ${PREDICT_PAYLOAD_EMPTY_DEVICE_ID}[deviceId]=  Set Variable  ${EMPTY}
    ${response}=    Post On Session  meditation-backend  ${PREDICT_URI}  json=${PREDICT_PAYLOAD_EMPTY_DEVICE_ID}
    ...                              expected_status=400

Retrain And Predict Again
    [Documentation]    Predict after new sessions were store and the model has been retrained several times.
    Post On Session  meditation-backend  ${MEDITAIONS_URI}  json=${TRAIN_MODEL_PAYLOAD}  expected_status=201
    Post On Session  meditation-backend  ${MEDITAIONS_URI}  json=${TRAIN_MODEL_PAYLOAD}  expected_status=201
    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  params=${DEVICE_ID_DICT}  expected_status=200
    Post On Session  meditation-backend  ${PREDICT_URI}  json=${PREDICT_PAYLOAD}  expected_status=200

Predict Unexpected Media Type
    [Documentation]    Send a request using a plain string instead of a JSON-formatted string.
    Post On Session  meditation-backend  ${PREDICT_URI}  data=my test string  expected_status=415

Train Unexpected Media Type
    [Documentation]    Send a request for storing session data using a plain string instead of a JSON-formatted string.
    Post On Session  meditation-backend  ${MEDITAIONS_URI}  data=my test string  expected_status=415

Train Empty Session Periods List
    [Documentation]    Sends a training request with an empty sessionPeriods list.
    [Tags]  PRIO2
    ${EMPTY_list}=  Create List
    ${TRAIN_PAYLOAD_EMPTY_SESSION_LIST}=  Copy Dictionary  ${TRAIN_MODEL_PAYLOAD}  deep_copy=${True}
    ${TRAIN_PAYLOAD_EMPTY_SESSION_LIST}[sessionPeriods]=  Set Variable  ${EMPTY_list}
    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  json=${TRAIN_PAYLOAD_EMPTY_SESSION_LIST}
    ...              expected_status=400

Predict Empty Session Periods List
    [Documentation]    Sends a prediction request with an empty sessionPeriods list.
    [Tags]  PRIO2
    ${EMPTY_list}=  Create List
    ${PREDICT_PAYLOAD_EMPTY_SESSION_LIST}=  Copy Dictionary  ${PREDICT_PAYLOAD}  deep_copy=${True}
    ${PREDICT_PAYLOAD_EMPTY_SESSION_LIST}[sessionPeriods]=  Set Variable  ${EMPTY_list}
    Post On Session  meditation-backend  ${PREDICT_URI}  json=${PREDICT_PAYLOAD_EMPTY_SESSION_LIST}
    ...              expected_status=400

Train Missing Period
    [Documentation]    Sends a training request with an incomplete sessionPeriods list.
    [Tags]  PRIO2
    ${TRAIN_PAYLOAD_MISSING_PERIOD}=  Copy Dictionary  ${TRAIN_MODEL_PAYLOAD}  deep_copy=${True}
    Remove From List    ${TRAIN_PAYLOAD_MISSING_PERIOD}[sessionPeriods]  0
    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  json=${TRAIN_PAYLOAD_MISSING_PERIOD}
    ...              expected_status=400

Predict Missing Period
    [Documentation]    Sends a prediction request with an incomplete sessionPeriods list.
    [Tags]  PRIO2
    ${PREDICT_PAYLOAD_MISSING_PERIOD}=  Copy Dictionary  ${PREDICT_PAYLOAD}  deep_copy=${True}
    Remove From List    ${PREDICT_PAYLOAD_MISSING_PERIOD}[sessionPeriods]  0
    Post On Session  meditation-backend  ${PREDICT_URI}  json=${PREDICT_PAYLOAD_MISSING_PERIOD}
    ...              expected_status=400

Train Missing Heart Rate Measurements
    [Documentation]    Sends a training request with an incomplete heartRateMeasurements list.
    [Tags]  PRIO2
    ${TRAIN_PAYLOAD_MISSING_HEART_RATES}=  Copy Dictionary  ${TRAIN_MODEL_PAYLOAD}  deep_copy=${True}
    Remove From List    ${TRAIN_PAYLOAD_MISSING_HEART_RATES}[sessionPeriods][0][heartRateMeasurements]  0
    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  json=${TRAIN_PAYLOAD_MISSING_HEART_RATES}
    ...              expected_status=400

PREDICT Missing Heart Rate Measurements
    [Documentation]    Sends a prediction request with an incomplete heartRateMeasurements list.
    [Tags]  PRIO2
    ${PREDICT_PAYLOAD_MISSING_HEART_RATES}=  Copy Dictionary  ${PREDICT_PAYLOAD}  deep_copy=${True}
    Remove From List    ${PREDICT_PAYLOAD_MISSING_HEART_RATES}[sessionPeriods][0][heartRateMeasurements]  0
    Post On Session  meditation-backend  ${PREDICT_URI}  json=${PREDICT_PAYLOAD_MISSING_HEART_RATES}
    ...              expected_status=400

*** Keywords ***
Generate UUID
    ${uuid}=  Generate Random String  length=10  chars=[LETTERS][NUMBERS][LOWER]
    [Return]    ${uuid}