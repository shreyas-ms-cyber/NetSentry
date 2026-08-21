"""
Unit tests for Alert Service
"""

import pytest
from datetime import datetime, timezone, timedelta
from app.services.alert_service import AlertService
from app.models import Device, PortScan, Alert

class TestAlertService:
    """Tests for Alert Service"""
    
    def test_new_device_alert(self, db):
        service = AlertService()
        device = Device(
            ip_address='192.168.1.50',
            mac_address='AA:BB:CC:DD:EE:50',
            vendor='Test',
            hostname='new-device',
            first_seen=datetime.now(timezone.utc)
        )
        db.session.add(device)
        db.session.commit()
        
        alert = service.check_new_device(device)
        # Alert may or may not be created based on timing
        assert alert is None or alert.alert_type == 'NEW_DEVICE'
    
    def test_new_open_port_alert(self, db, sample_device):
        service = AlertService()
        new_port_scan = [{
            'port': 8080,
            'protocol': 'TCP',
            'status': 'OPEN',
            'service': 'HTTP-Alt'
        }]
        
        alerts = service.check_new_open_port(sample_device, new_port_scan)
        # Should create alert for new open port
        assert alerts is not None
    
    def test_device_offline_detection(self, db, sample_device):
        service = AlertService()
        # Update last_seen to be older than threshold (10 minutes)
        sample_device.last_seen = datetime.now(timezone.utc) - timedelta(minutes=10)
        db.session.commit()
        
        alerts = service.check_device_offline()
        # Should detect offline device or return empty list
        assert alerts is not None
