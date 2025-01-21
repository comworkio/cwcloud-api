from unittest import TestCase, mock
from datetime import datetime
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID

from entities.Monitor import Monitor
from controllers.monitor import get_monitors, get_monitor, add_monitor, update_monitor, remove_monitor
from schemas.Monitor import MonitorSchema
from utils.observability.monitor import check_status_code_pattern, not_match_tcp_url_format

class TestMonitor(TestCase):
    def setUp(self):
        self.mock_db = mock.Mock(spec=Session)
        self.mock_user = mock.Mock()
        self.mock_user.id = 1
        self.mock_user.is_admin = False
        
        self.sample_monitor_id = "550e8400-e29b-41d4-a716-446655440000"
        self.sample_monitor = Monitor(
            id=UUID(self.sample_monitor_id),
            user_id=1,
            type="http",
            name="test-monitor",
            hash="abc123",
            url="http://example.com",
            method="GET",
            expected_http_code="200",
            created_at=datetime.now().date().strftime('%Y-%m-%d'),
            updated_at=datetime.now().date().strftime('%Y-%m-%d')
        )

        self.original_get_user_monitors = Monitor.getUserMonitors

    def tearDown(self):
        Monitor.getUserMonitors = self.original_get_user_monitors

    def test_check_status_code_pattern_200(self):
        self.assertTrue(check_status_code_pattern(200, '20*'))

    def test_check_status_code_pattern_201(self):
        self.assertTrue(check_status_code_pattern(201, '20*'))

    def test_check_status_code_pattern_400_ko(self):
        self.assertFalse(check_status_code_pattern(400, '20*'))

    def test_check_status_code_pattern_exact_match(self):
        self.assertTrue(check_status_code_pattern(404, '404'))

    def test_check_status_code_pattern_no_match(self):
        self.assertFalse(check_status_code_pattern(301, '404'))

    def test_valid_tcp_url(self):
        self.assertFalse(not_match_tcp_url_format("localhost:8080"))
        
    def test_invalid_tcp_url_no_port(self):
        self.assertTrue(not_match_tcp_url_format("localhost"))
        
    def test_invalid_tcp_url_wrong_format(self):
        self.assertTrue(not_match_tcp_url_format("tcp://localhost:8080"))

    def test_get_monitors_success(self):
        Monitor.getUserMonitors = mock.Mock(return_value=[self.sample_monitor])
        
        result = get_monitors(self.mock_user, self.mock_db)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "test-monitor")

    def test_get_monitors_with_family(self):
        monitor_with_family = self.sample_monitor
        monitor_with_family.family = "test_family"

        Monitor.getUserMonitors = mock.Mock(return_value=[monitor_with_family])
        
        result = get_monitors(self.mock_user, self.mock_db, family="test_family")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].family, "test_family")

    def test_get_monitor_success(self):
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.sample_monitor
        result = get_monitor(self.mock_user, self.sample_monitor_id, self.mock_db)
        self.assertEqual(result.name, "test-monitor")

    def test_get_monitor_not_found(self):
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = get_monitor(self.mock_user, self.sample_monitor_id, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 404)

    def test_add_monitor_success(self):
        payload = MonitorSchema(
            type="http",
            name="new-monitor",
            url="http://example.com",
            method="GET",
            expected_http_code="200"
        )
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = add_monitor(self.mock_user, payload, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 201)

    def test_add_monitor_invalid_http_code(self):
        Monitor.getUserMonitors = mock.Mock(return_value=[])
        
        payload = MonitorSchema(
            type="http",
            name="new-monitor",
            url="http://example.com",
            method="GET",
            expected_http_code="999"
        )
        result = add_monitor(self.mock_user, payload, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 400)

    def test_add_monitor_invalid_tcp_url(self):
        Monitor.getUserMonitors = mock.Mock(return_value=[])
        
        payload = MonitorSchema(
            type="tcp",
            name="new-monitor",
            url="invalid-tcp-url",
            method="GET",
            expected_http_code="200"
        )
        result = add_monitor(self.mock_user, payload, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 400)

    def test_update_monitor_success(self):
        payload = MonitorSchema(
            type="http",
            name="updated-monitor",
            url="http://example.com",
            method="GET",
            expected_http_code="200"
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.sample_monitor
        
        result = update_monitor(self.mock_user, self.sample_monitor_id, payload, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 200)

    def test_update_monitor_not_found(self):
        payload = MonitorSchema(
            type="http",
            name="updated-monitor",
            url="http://example.com",
            method="GET",
            expected_http_code="200"
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = update_monitor(self.mock_user, self.sample_monitor_id, payload, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 404)

    def test_remove_monitor_success(self):
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.sample_monitor
        result = remove_monitor(self.mock_user, self.sample_monitor_id, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 200)

    def test_remove_monitor_not_found(self):
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = remove_monitor(self.mock_user, self.sample_monitor_id, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 404)
