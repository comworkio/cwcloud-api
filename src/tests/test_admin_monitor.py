from unittest import TestCase, mock
from datetime import datetime
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID

from entities.Monitor import Monitor
from controllers.admin.admin_monitor import get_monitors, get_monitor, add_monitor, update_monitor, remove_monitor
from schemas.Monitor import AdminMonitorSchema

class TestMonitorAdmin(TestCase):
    def setUp(self):
        self.mock_db = mock.Mock(spec=Session)
        self.mock_admin_user = mock.Mock()
        self.mock_admin_user.id = 1
        self.mock_admin_user.is_admin = True

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

    def test_get_monitors_for_admin(self):
        Monitor.getAllMonitors = mock.Mock(return_value=[self.sample_monitor])
        
        result = get_monitors(self.mock_db)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "test-monitor")

    def test_get_monitor_for_admin(self):
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.sample_monitor
        
        result = get_monitor(self.sample_monitor_id, self.mock_db)
        self.assertEqual(result.name, "test-monitor")

    def test_add_monitor_for_admin(self):
        payload = AdminMonitorSchema(
            type="http",
            name="new-monitor",
            url="http://example.com",
            method="GET",
            expected_http_code="200",
            user_id=self.mock_admin_user.id
        )
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = add_monitor(payload, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 201)

    def test_update_monitor_for_admin(self):
        payload = AdminMonitorSchema(
            type="http",
            name="updated-monitor",
            url="http://example.com",
            method="GET",
            expected_http_code="200",
            user_id=self.mock_admin_user.id
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.sample_monitor
        
        result = update_monitor(self.sample_monitor_id, payload, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 200)

    def test_remove_monitor_for_admin(self):
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.sample_monitor
        result = remove_monitor(self.sample_monitor_id, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 200)

    def test_remove_monitor_for_admin_not_found(self):
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = remove_monitor(self.sample_monitor_id, self.mock_db)
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 404)
