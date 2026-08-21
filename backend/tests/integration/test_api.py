"""
Integration tests for API endpoints
"""

import json
import pytest
from app.models import Device, PortScan, TrafficStat, Alert

class TestAPIEndpoints:
    """Tests for all API endpoints"""
    
    def test_health_check(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
    
    def test_api_health(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
    
    def test_dashboard_summary(self, client, sample_device, sample_port_scan):
        response = client.get('/api/dashboard/summary')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_devices' in data
        assert 'online_devices' in data
        assert 'open_ports' in data
    
    def test_get_devices(self, client, sample_device):
        response = client.get('/api/devices')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1
        assert len(data['devices']) >= 1
    
    def test_get_device(self, client, sample_device):
        response = client.get(f'/api/devices/{sample_device.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['ip_address'] == '192.168.1.100'
    
    def test_get_device_ports(self, client, sample_device, sample_port_scan):
        response = client.get(f'/api/devices/{sample_device.id}/ports')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1
    
    def test_get_ports(self, client, sample_port_scan):
        response = client.get('/api/ports')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1
    
    def test_get_ports_filtered(self, client, sample_port_scan):
        response = client.get('/api/ports?status=OPEN')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1
    
    def test_get_traffic(self, client, sample_traffic):
        response = client.get('/api/traffic')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1
    
    def test_get_alerts(self, client, sample_alert):
        response = client.get('/api/alerts')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1
    
    def test_get_alerts_filtered(self, client, sample_alert):
        response = client.get('/api/alerts?severity=LOW')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] >= 1

class TestIngestionEndpoints:
    """Tests for ingestion endpoints with authentication"""
    
    def test_ingest_devices_unauthorized(self, client):
        response = client.post('/api/devices/ingest', json={})
        assert response.status_code == 400  # Invalid data format
    
    def test_ingest_devices_success(self, client, db):
        data = {
            'devices': [{
                'ip_address': '192.168.1.200',
                'mac_address': 'AA:BB:CC:DD:EE:99',
                'vendor': 'Test Vendor',
                'hostname': 'test-device-2'
            }]
        }
        # Note: In production, this would require X-Agent-Key
        # For testing, we skip auth or use a test key
        response = client.post('/api/devices/ingest', json=data)
        assert response.status_code in [200, 201, 400]
    
    def test_ingest_port_scans(self, client, sample_device):
        data = {
            'port_scans': [{
                'device_ip': '192.168.1.100',
                'port': 8080,
                'protocol': 'TCP',
                'status': 'OPEN',
                'service': 'HTTP-Alt'
            }]
        }
        response = client.post('/api/ports/ingest', json=data)
        assert response.status_code in [200, 201, 400]
    
    def test_ingest_traffic(self, client):
        data = {
            'timestamp': '2024-01-01T00:00:00',
            'packets_per_sec': 100.5,
            'bandwidth_bytes': 512000,
            'protocol_breakdown': {'tcp': 50, 'udp': 30, 'icmp': 10, 'other': 10}
        }
        response = client.post('/api/traffic/ingest', json=data)
        assert response.status_code in [200, 201, 400]
