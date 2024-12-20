from unittest import TestCase
from utils.observability.tracker import parse_user_agent

class TestTracker(TestCase):
    def init(self, *args, **kwargs):
        super(TestTracker, self).__init__(*args, **kwargs)

    def test_parse_user_agent_nominal(self):
        ## Given
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"

        #When
        result = parse_user_agent(user_agent)

        ## Then
        self.assertEqual(result['os'], "windows")
        self.assertEqual(result['device'], "computer")
        self.assertEqual(result['browser'], "chrome")

    def test_parse_user_agent_empty(self):
        ## Given
        user_agent = ""

        #When
        result = parse_user_agent(user_agent)

        ## Then
        self.assertEqual(result['os'], "unknown")
        self.assertEqual(result['device'], "unknown")
        self.assertEqual(result['browser'], "unknown")

    def test_parse_user_agent_undefined(self):
        ## Given
        user_agent = "whatever"

        #When
        result = parse_user_agent(user_agent)

        ## Then
        self.assertEqual(result['os'], "unknown")
        self.assertEqual(result['device'], "unknown")
        self.assertEqual(result['browser'], "unknown")
