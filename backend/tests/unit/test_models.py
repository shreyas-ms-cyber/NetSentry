"""
Unit tests for database models
"""

import pytest
from app.models import Device, PortScan, TrafficStat, Alert
from datetime import datetime

class TestDeviceModel:
    """Tests for Device model"""
    
    def test_create_device(self, db):
        device = Device(
            ip_address='192.168.1.1',
            mac_address='00:11:22:33:44:55',
            vendor='Cisco',
            hostname='router'
        )
        db.session.add(device)
        db.session.commit()
        
        assert device.id is not None
        assert device.ip_address == '192.168.1.1'
        assert device.status == 'ONLINE'
        assert device.first_seen is not None
    
    def test_device_to_dict(self, sample_device):
        device_dict = sample_device.to_dict()
        assert device_dict['ip_address'] == '192.168.1.100'
        assert device_dict['hostname'] == 'test-device'
        assert 'id' in device_dict
        assert 'first_seen' in device_dict
    
    def test_device_port_relationship(self, db, sample_device, sample_port_scan):
        assert len(sample_device.port_scans.all()) > 0
        assert sample_device.port_scans.first().port == 80

class TestPortScanModel:
    """Tests for PortScan model"""
    
    def test_create_port_scan(self, db, sample_device):
        port_scan = PortScan(
            device_id=sample_device.id,
            port=443,
            protocol='TCP',
            status='OPEN'
        )
        db.session.add(port_scan)
        db.session.commit()
        
        assert port_scan.id is not None
        assert port_scan.port == 443
        assert port_scan.status == 'OPEN'
    
    def test_port_scan_to_dict(self, sample_port_scan):
        port_dict = sample_port_scan.to_dict()
        assert port_dict['port'] == 80
        assert port_dict['protocol'] == 'TCP'
        assert port_dict['status'] == 'OPEN'

class TestTrafficStatModel:
    """Tests for TrafficStat model"""
    
    def test_create_traffic_stat(self, db):
        traffic = TrafficStat(
            packets_per_sec=200.5,
            bandwidth_bytes=2048000,
            protocol_breakdown={'tcp': 70, 'udp': 20, 'icmp': 10, 'other': 0}
        )
        db.session.add(traffic)
        db.session.commit()
        
        assert traffic.id is not None
        assert traffic.packets_per_sec == 200.5
        assert traffic.protocol_breakdown['tcp'] == 70
    
    def test_traffic_stat_to_dict(self, sample_traffic):
        traffic_dict = sample_traffic.to_dict()
        assert traffic_dict['packets_per_sec'] == 150.5
        assert traffic_dict['bandwidth_mbps'] > 0

class TestAlertModel:
    """Tests for Alert model"""
    
    def test_create_alert(self, db, sample_device):
        alert = Alert(
            alert_type='NEW_OPEN_PORT',
            device_id=sample_device.id,
            description='New open port detected on 192.168.1.100:8080/TCP',
            severity='MEDIUM'
        )
        db.session.add(alert)
        db.session.commit()
        
        assert alert.id is not None
        assert alert.alert_type == 'NEW_OPEN_PORT'
        assert alert.severity == 'MEDIUM'
        assert alert.acknowledged == False
    
    def test_alert_to_dict(self, sample_alert):
        alert_dict = sample_alert.to_dict()
        assert alert_dict['alert_type'] == 'NEW_DEVICE'
        assert alert_dict['severity'] == 'LOW'
        assert alert_dict['acknowledged'] == False
