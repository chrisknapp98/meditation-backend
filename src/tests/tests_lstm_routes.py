import unittest


class LSTMRoutesTest(unittest.TestCase):

    def setUp(self) -> None:
        # setup your stuff here
        pass

    def tearDown(self) -> None:
        pass

    def test_map_data(self):
        test_list = ["this-test1-big-string", "test2"]
        self.assertEqual(len(test_list), 2)
