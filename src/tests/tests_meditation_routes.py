import copy
import unittest

from routes import meditation_routes


class MeditationRoutesTest(unittest.TestCase):
    MEDITATION_DATA: dict = {
        "deviceId": '6f9e2b1c-4a8d-4935-91b8-2e5bf4aef8d7',
        "date": "2019-11-24T15:00:00.000Z",
        "duration": 3600,
        "isCompleted": True,
        "isCanceled": False,
        "sessionPeriods": [
            {
                "heartRateMeasurements": [
                    {"date": "2024-01-01T21:47:31.000Z", "heartRate": 110.0},
                    {"date": "2024-01-01T21:47:33.000Z", "heartRate": 107.5},
                    {"date": "2024-01-01T21:47:35.000Z", "heartRate": 105.0},
                    {"date": "2024-01-01T21:47:37.000Z", "heartRate": 102.5},
                    {"date": "2024-01-01T21:47:39.000Z", "heartRate": 100.0},
                    {"date": "2024-01-01T21:47:41.000Z", "heartRate": 97.5},
                    {"date": "2024-01-01T21:47:43.000Z", "heartRate": 95.0},
                    {"date": "2024-01-01T21:47:45.000Z", "heartRate": 92.5},
                    {"date": "2024-01-01T21:47:47.000Z", "heartRate": 90.0},
                    {"date": "2024-01-01T21:47:49.000Z", "heartRate": 87.5},
                    {"date": "2024-01-01T21:47:51.000Z", "heartRate": 85.0},
                    {"date": "2024-01-01T21:47:53.000Z", "heartRate": 82.5},
                    {"date": "2024-01-01T21:47:55.000Z", "heartRate": 80.0},
                    {"date": "2024-01-01T21:47:57.000Z", "heartRate": 77.5},
                    {"date": "2024-01-01T21:47:59.000Z", "heartRate": 75.0}
                ],
                "visualization": "nature",
                "beatFrequency": 500,
                "breathingPattern": [
                    {"inhale": 4},
                    {"hold": 7},
                    {"exhale": 8},
                    {"hold": None}
                ],
                "breathingPatternMultiplier": 1,
                "isHapticFeedbackEnabled": True
            }],
        "visualization": "nature",
        "beatFrequency": 500,
        "breathingPattern": [
            {"inhale": 4},
            {"hold": 7},
            {"exhale": 8},
            {"hold": None}
        ],
        "breathingPatternMultiplier": 1,
        "isHapticFeedbackEnabled": True
    }

    def setUp(self) -> None:
        self.meditation_data = copy.deepcopy(MeditationRoutesTest.MEDITATION_DATA)

    def test_validate_meditation_session_data_good(self):
        res = meditation_routes.validate_meditation_session_data(self.meditation_data)
        self.assertEqual(self.meditation_data, res[0])

    def test_validate_meditation_session_data_missing_field(self):
        self.meditation_data.pop('deviceId')
        res = meditation_routes.validate_meditation_session_data(self.meditation_data)
        self.assertEqual((None, ({'error': 'Missing required field: deviceId'}, 400)), res)

    def test_validate_meditation_session_data_empty_device_id(self):
        self.meditation_data['deviceId'] = str()
        res = meditation_routes.validate_meditation_session_data(self.meditation_data)
        self.assertEqual((None, ({'error': 'Device ID is empty. Please provide a valid device ID.'}, 400)), res)

    def test_validate_meditation_session_data_empty_session_periods_list(self):
        self.meditation_data['sessionPeriods'] = []
        res = meditation_routes.validate_meditation_session_data(self.meditation_data)
        self.assertEqual((None, ({'error': f'Session period list is empty.'}, 400)), res)

    def test_validate_meditation_session_data_missing_key_in_session_periods_list(self):
        self.meditation_data['sessionPeriods'][0].pop('visualization')
        res = meditation_routes.validate_meditation_session_data(self.meditation_data)
        self.assertEqual((None,
                          ({'error': "Missing required field 'visualization' in session period at index 0"}, 400)),
                         res)

    def test_validate_meditation_session_data_missing_key_in_heart_rate_measurements_list(self):
        self.meditation_data['sessionPeriods'][0]['heartRateMeasurements'][0].pop('date')
        res = meditation_routes.validate_meditation_session_data(self.meditation_data)
        self.assertEqual((None,
                          ({'error': "Missing required field 'date' in heart rate measurement at index "
                                     '0 in session period at index 0'}, 400)),
                         res)
