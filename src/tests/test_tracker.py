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

    def test_parse_user_agent_ipad(self):
        ## Given
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"

        #When
        result = parse_user_agent(user_agent)

        ## Then
        self.assertEqual(result['os'], "macos")
        self.assertEqual(result['device'], "computer")
        self.assertEqual(result['browser'], "safari")
        self.assertEqual(result['details']['brand'], "apple")
        self.assertEqual(result['details']['type'], "macos")

    def test_parse_user_agent_iphone(self):
        ## Given
        user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Mobile/15E148 Safari/604.1"

        #When
        result = parse_user_agent(user_agent)

        ## Then
        self.assertEqual(result['os'], "ios")
        self.assertEqual(result['device'], "mobile")
        self.assertEqual(result['browser'], "safari")
        self.assertEqual(result['details']['brand'], "apple")
        self.assertEqual(result['details']['type'], "iphone")

    def test_parse_user_agent_smarttv(self):
        ## Given
        user_agent = "Mozilla/5.0 (SMART-TV; Linux; Tizen 2.3) AppleWebkit/538.1 (KHTML, like Gecko) SamsungBrowser/1.0 TV Safari/538.11"

        #When
        result = parse_user_agent(user_agent)

        ## Then
        self.assertEqual(result['os'], "linux")
        self.assertEqual(result['device'], "smarttv")
        self.assertEqual(result['browser'], "samsung")
        self.assertEqual(result['details']['brand'], "samsung")
        self.assertEqual(result['details']['type'], "smarttv")

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
