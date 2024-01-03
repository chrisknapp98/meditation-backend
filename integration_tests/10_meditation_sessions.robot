
*** Variables ***

${BACKEND_URL}  DEFINE_IN_VARIABLES_FILE
${DEVICE_ID}  RANDOMLY_GENERATED
${TRAIN_MODEL_PAYLOAD}  DEFINE_IN_VARIABLES_FILE
${PREDICT_PAYLOAD}  DEFINE_IN_VARIABLES_FILE
${MEDITAIONS_URI}  /meditations
${TRAIN_MODEL_URI}  /train_model
${PREDDICT_URI}  /predict
&{DEVICER_ID_DICT}  deviceId=${DEVICE_ID}

${NO_MEDITAIONS_FOUND_TEXT}  No meditation sessions found
${MODEL_TRAINED_TEXT}  Model for device {device_id} trained successfully.
${NO_PREVIOUS_SESSION_FOUND}   Model for device {device_id} not trained. No previous session found.

*** Settings ***
Library    RequestsLibrary
Library    String
Library    Collections

Suite Setup    Create Session  meditation-backend  ${BACKEND_URL}

*** Test Cases ***
Generate UUID
    ${DEVICE_ID}=    Generate UUID
    Log    Generated UUID: ${DEVICE_ID}
    Set Suite Variable  ${DEVICE_ID}
    ${TRAIN_MODEL_PAYLOAD}=  Set To Dictionary    ${TRAIN_MODEL_PAYLOAD}  deviceId=${DEVICE_ID}
    ${PREDICT_PAYLOAD}=  Set To Dictionary    ${TRAIN_MODEL_PAYLOAD}  deviceId=${DEVICE_ID}

Get All Sessions By Device Id No Sessions Created
    ${response}=    GET On Session  meditation-backend  ${MEDITAIONS_URI}  params=${DEVICER_ID_DICT}
    ...                             expected_status=404
    Should Be Equal  ${NO_MEDITAIONS_FOUND_TEXT}  ${response.json()}[message]

Get All Sessions Empty Id
    ${EMPTY_DEVICE_ID}=  Create Dictionary  deviceId=
    ${response}=    GET On Session  meditation-backend  ${MEDITAIONS_URI}  params=${EMPTY_DEVICE_ID}
    ...                             expected_status=400

Predict Before Sessions Stored
    ${response}=    Post On Session  meditation-backend  ${PREDDICT_URI}  json=${PREDICT_PAYLOAD}
    ...                              expected_status=200
    ${recommended_parameters}=  Set Variable  ${response.json()}[bestCombination]

    Dictionary Should Contain Key  ${recommended_parameters}  beatFrequency
    Dictionary Should Contain Key  ${recommended_parameters}  breathingPatternMultiplier
    Dictionary Should Contain Key  ${recommended_parameters}  visualization

Train Model No Previous Session
    ${response}=    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  json=${TRAIN_MODEL_PAYLOAD}
    ...                             expected_status=200
    ${EXPECTED_MESSAGE}=  Format String  ${NO_PREVIOUS_SESSION_FOUND}  device_id=${DEVICE_ID}
    Should Be Equal  ${EXPECTED_MESSAGE}  ${response.json()}[message]

Train Model
    ${response}=    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  json=${TRAIN_MODEL_PAYLOAD}
    ...                             expected_status=200
    ${EXPECTED_MESSAGE}=  Format String  ${MODEL_TRAINED_TEXT}  device_id=${DEVICE_ID}
    Should Be Equal  ${EXPECTED_MESSAGE}  ${response.json()}[message]

Train Model Empty Device Id
    ${TRAIN_MODEL_EMPTY_DEVICE_ID}=  Set To Dictionary    ${TRAIN_MODEL_PAYLOAD}  deviceId=
    ${response}=    Post On Session  meditation-backend  ${TRAIN_MODEL_URI}  json=${TRAIN_MODEL_EMPTY_DEVICE_ID}
    ...                             expected_status=400

Predict After Training
    ${response}=    Post On Session  meditation-backend  ${PREDDICT_URI}  json=${PREDICT_PAYLOAD}
    ...                              expected_status=200
    ${recommended_parameters}=  Set Variable  ${response.json()}[bestCombination]

    Dictionary Should Contain Key  ${recommended_parameters}  beatFrequency
    Dictionary Should Contain Key  ${recommended_parameters}  breathingPatternMultiplier
    Dictionary Should Contain Key  ${recommended_parameters}  visualization

 Predict Empty Device Id
    ${PREDICT_PAYLOAD_EMPTY_DEVICE_ID}=  Set To Dictionary    ${PREDICT_PAYLOAD}  deviceId=
    ${response}=    Post On Session  meditation-backend  ${PREDDICT_URI}  json=${PREDICT_PAYLOAD}
    ...                              expected_status=400

*** Keywords ***
Generate UUID
    ${uuid}=  Generate Random String  length=10  chars=[LETTERS][NUMBERS][LOWER]
    [Return]    ${uuid}