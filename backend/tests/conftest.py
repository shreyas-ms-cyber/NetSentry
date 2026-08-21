"""
Pytest configuration for NetSentry Backend
"""

import pytest
import sys
import os

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db as _db
from app.models import Device, PortScan, TrafficStat, Alert

@pytest.fixture
def app():
    """Create a Flask app for testing"""
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def db(app):
    """Get database instance"""
    with app.app_context():
        yield _db

@pytest.fixture
def sample_device(db):
    """Create a sample device for testing"""
    device = Device(
        ip_address='192.168.1.100',
        mac_address='AA:BB:CC:DD:EE:FF',
        vendor='Test Vendor',
        hostname='test-device',
        status='ONLINE'
    )
    db.session.add(device)
    db.session.commit()
    return device

@pytest.fixture
def sample_port_scan(db, sample_device):
    """Create a sample port scan for testing"""
    port_scan = PortScan(
        device_id=sample_device.id,
        port=80,
        protocol='TCP',
        status='OPEN'
    )
    db.session.add(port_scan)
    db.session.commit()
    return port_scan

@pytest.fixture
def sample_traffic(db):
    """Create a sample traffic stat for testing"""
    traffic = TrafficStat(
        packets_per_sec=150.5,
        bandwidth_bytes=1024000,
        protocol_breakdown={'tcp': 60, 'udp': 30, 'icmp': 5, 'other': 5}
    )
    db.session.add(traffic)
    db.session.commit()
    return traffic

@pytest.fixture
def sample_alert(db, sample_device):
    """Create a sample alert for testing"""
    alert = Alert(
        alert_type='NEW_DEVICE',
        device_id=sample_device.id,
        description='New device joined the network: 192.168.1.100',
        severity='LOW'
    )
    db.session.add(alert)
    db.session.commit()
    return alert
