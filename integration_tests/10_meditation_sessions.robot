
*** Variables ***

${BACKEND_URL}  DEFINE_IN_VARIABLES_FILE
${DEVICE_ID}  RANDOMLY_GENERATED
${TRAIN_MODEL_PAYLOAD}  DEFINE_IN_VARIABLES_FILE
${PREDICT_PAYLOAD}  DEFINE_IN_VARIABLES_FILE
${MEDITAIONS_URI}  /meditations
${TRAIN_MODEL_URI}  /train_model
${PREDDICT_URI}  /predict
&{DEVICE_ID_DICT}  deviceId=${DEVICE_ID}

${NO_MEDITAIONS_FOUND_TEXT}  No meditation sessions found
${MODEL_TRAINED_TEXT}  Model for device {device_id} trained successfully.
${NO_PREVIOUS_SESSION_FOUND}   Model for device {device_id} not trained. No previous session found.
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

Get All Sessions By Device Id No Sessions Created
    [Documentation]  Get all sessions for a device id which has no data stored yet.
    ${response}=    GET On Session  meditation-backend  ${MEDITAIONS_URI}  params=${DEVICE_ID_DICT}
    ...                             expected_status=404
    Should Be Equal  ${NO_MEDITAIONS_FOUND_TEXT}  ${response.json()}[message]

Predict Before Sessions Stored
    [Documentation]  Tries to get a prediction before the model was trained. Should fail, because there is not enough
    ...              data yet to make predictions.
    ${response}=    Post On Session  meditation-backend  ${PREDDICT_URI}  json=${PREDICT_PAYLOAD}
    ...                              expected_status=200
    ${EXPECTED_MESSAGE}=  Format String  ${NOT_ENOUGH_DATA_TEXT}  device_id=${DEVICE_ID}
    Should Be Equal  ${EXPECTED_MESSAGE}  ${response.json()}[message]

Train Model No Previous Session
    [Documentation]  Sends the first chunk of training data. The backend should respond, that no previous data was found.
    ${response}=    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  json=${TRAIN_MODEL_PAYLOAD}
    ...                             expected_status=200
    ${EXPECTED_MESSAGE}=  Format String  ${NO_PREVIOUS_SESSION_FOUND}  device_id=${DEVICE_ID}
    Should Be Equal  ${EXPECTED_MESSAGE}  ${response.json()}[message]

Train Model
    [Documentation]  Send the second chunk of training data. Since there is already data stored in the database, there
    ...              should be no additional hint.
    ${response}=    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  json=${TRAIN_MODEL_PAYLOAD}
    ...                             expected_status=200
    ${EXPECTED_MESSAGE}=  Format String  ${MODEL_TRAINED_TEXT}  device_id=${DEVICE_ID}
    Should Be Equal  ${EXPECTED_MESSAGE}  ${response.json()}[message]

Train Model Empty Device Id
    [Documentation]  Sends a training payload with an empty device id. The server should respond with an error.
    ${TRAIN_MODEL_EMPTY_DEVICE_ID}=  Set To Dictionary    ${TRAIN_MODEL_PAYLOAD}  deviceId=
    ${response}=    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  json=${TRAIN_MODEL_EMPTY_DEVICE_ID}
    ...                             expected_status=400

Predict After Training
    [Documentation]  Sends a request to get a prediction after the model has been trained with sufficient data.
    ...              Additionally, validates whether all expected keys are present in the response JSON.
    ${response}=    Post On Session  meditation-backend  ${PREDDICT_URI}  json=${PREDICT_PAYLOAD}
    ...                              expected_status=200
    ${recommended_parameters}=  Set Variable  ${response.json()}[bestCombination]

    Dictionary Should Contain Key  ${recommended_parameters}  beatFrequency
    Dictionary Should Contain Key  ${recommended_parameters}  breathingPatternMultiplier
    Dictionary Should Contain Key  ${recommended_parameters}  visualization

 Predict Empty Device Id
    [Documentation]    Sends a prediction payload with an empty device id. The server should respond with an error.
    ${PREDICT_PAYLOAD_EMPTY_DEVICE_ID}=  Set To Dictionary    ${PREDICT_PAYLOAD}  deviceId=
    ${response}=    Post On Session  meditation-backend  ${PREDDICT_URI}  json=${PREDICT_PAYLOAD}
    ...                              expected_status=400

*** Keywords ***
Generate UUID
    ${uuid}=  Generate Random String  length=10  chars=[LETTERS][NUMBERS][LOWER]
    [Return]    ${uuid}