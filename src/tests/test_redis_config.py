from unittest import TestCase
from utils.redis_config import get_host_and_port

class TestRedisConfig(TestCase):
    def test_url_nominal(self):
        # Given
        url = "redis_host:1234"

        # When
        host, port = get_host_and_port(url)

        # Then
        self.assertEqual(host, "redis_host")
        self.assertEqual(port, 1234)

    def test_url_without_port(self):
        # Given
        url = "redis_host"

        # When
        host, port = get_host_and_port(url)

        # Then
        self.assertEqual(host, "redis_host")
        self.assertEqual(port, 6379)
