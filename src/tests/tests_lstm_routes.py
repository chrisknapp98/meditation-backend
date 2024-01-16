import unittest

from routes import lstm_routes


class LSTMRoutesTest(unittest.TestCase):
    SESSION_PERIODS: list[dict] = [{
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
    }]

    EXPECTED_TRAINING_DATA = [
        [110.0, 107.5, 105.0, 102.5, 100.0, 97.5, 95.0, 92.5, 90.0, 87.5, 85.0, 82.5, 80.0, 77.5, 75.0],
        [500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500],
        [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

    def test_get_visualization_number_good(self):
        self.assertEqual(0, lstm_routes.get_visualization_number('Arctic'))

    def test_get_visualization_number_which_does_not_exist(self):
        self.assertRaises(KeyError, lstm_routes.get_visualization_number, 'notExisting')

    def test_get_visualization_name_good(self):
        self.assertEqual(lstm_routes.Visualization.Skyline.name, lstm_routes.get_visualization_name(9))

    def test_get_visualization_name_value_does_not_exist(self):
        self.assertRaises(ValueError, lstm_routes.get_visualization_name, 10)

    def test_map_session_periods_to_training_data_good(self):
        res = lstm_routes.map_session_periods_to_prediction_array(LSTMRoutesTest.SESSION_PERIODS)
        self.assertEqual(LSTMRoutesTest.EXPECTED_TRAINING_DATA, res)
