"""
Alert Service - Automatic alert generation for network changes
"""

import logging
from datetime import datetime, timezone, timedelta
from app.extensions import db
from app.models import Device, PortScan, Alert

logger = logging.getLogger(__name__)

class AlertService:
    """Service for generating and managing alerts"""
    
    # Alert types
    ALERT_NEW_DEVICE = 'NEW_DEVICE'
    ALERT_NEW_OPEN_PORT = 'NEW_OPEN_PORT'
    ALERT_DEVICE_OFFLINE = 'DEVICE_OFFLINE'
    ALERT_DEVICE_ONLINE = 'DEVICE_ONLINE'
    
    # Severity levels
    SEVERITY_LOW = 'LOW'
    SEVERITY_MEDIUM = 'MEDIUM'
    SEVERITY_HIGH = 'HIGH'
    
    def __init__(self):
        self.offline_threshold_minutes = 5  # Configurable
    
    def check_new_device(self, device):
        """
        Check if this is a new device and generate alert
        
        Args:
            device: Device object
            
        Returns:
            Alert object or None
        """
        # Check if device was created recently (within the last minute)
        if device.first_seen:
            time_since_creation = datetime.now(timezone.utc) - device.first_seen
            if time_since_creation.total_seconds() < 120:  # Within 2 minutes
                # Check if alert already exists for this device
                existing = Alert.query.filter_by(
                    device_id=device.id,
                    alert_type=self.ALERT_NEW_DEVICE
                ).first()
                
                if not existing:
                    alert = Alert(
                        alert_type=self.ALERT_NEW_DEVICE,
                        device_id=device.id,
                        description=f"New device joined the network: {device.ip_address} ({device.hostname or 'Unknown'})",
                        severity=self.SEVERITY_LOW,
                        timestamp=datetime.now(timezone.utc)
                    )
                    db.session.add(alert)
                    db.session.commit()
                    logger.info(f"🔔 New Device Alert: {device.ip_address}")
                    return alert
        
        return None
    
    def check_new_open_port(self, device, new_port_scans):
        """
        Check for new open ports on existing devices
        
        Args:
            device: Device object
            new_port_scans: List of new port scan results
            
        Returns:
            list: Alert objects
        """
        alerts = []
        
        for scan in new_port_scans:
            if scan.get('status') != 'OPEN':
                continue
            
            port = scan.get('port')
            protocol = scan.get('protocol', 'TCP')
            service = scan.get('service')
            
            # Check if this port was previously open
            previous_scan = PortScan.query.filter_by(
                device_id=device.id,
                port=port,
                protocol=protocol,
                status='OPEN'
            ).order_by(PortScan.scanned_at.desc()).first()
            
            # If no previous OPEN scan exists, this is a new open port
            if not previous_scan:
                # Check if alert already exists for this device/port
                existing = Alert.query.filter_by(
                    device_id=device.id,
                    alert_type=self.ALERT_NEW_OPEN_PORT
                ).filter(
                    Alert.description.contains(f"port {port}/{protocol}")
                ).first()
                
                if not existing:
                    service_text = f" - {service}" if service else ""
                    alert = Alert(
                        alert_type=self.ALERT_NEW_OPEN_PORT,
                        device_id=device.id,
                        description=f"New open port detected: {device.ip_address}:{port}/{protocol}{service_text}",
                        severity=self.SEVERITY_MEDIUM,
                        timestamp=datetime.now(timezone.utc)
                    )
                    db.session.add(alert)
                    alerts.append(alert)
                    logger.info(f"🔔 New Open Port Alert: {device.ip_address}:{port}/{protocol}")
        
        if alerts:
            db.session.commit()
        
        return alerts
    
    def check_device_offline(self):
        """
        Check for devices that have gone offline
        
        Returns:
            list: Alert objects
        """
        alerts = []
        threshold_time = datetime.now(timezone.utc) - timedelta(minutes=self.offline_threshold_minutes)
        
        # Find devices that were online but haven't been seen recently
        offline_candidates = Device.query.filter_by(status='ONLINE').filter(
            Device.last_seen < threshold_time
        ).all()
        
        for device in offline_candidates:
            # Check if alert already exists for this device that's not acknowledged
            existing = Alert.query.filter_by(
                device_id=device.id,
                alert_type=self.ALERT_DEVICE_OFFLINE,
                acknowledged=False
            ).first()
            
            if not existing:
                device.status = 'OFFLINE'
                alert = Alert(
                    alert_type=self.ALERT_DEVICE_OFFLINE,
                    device_id=device.id,
                    description=f"Device went offline: {device.ip_address} ({device.hostname or 'Unknown'})",
                    severity=self.SEVERITY_HIGH,
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(alert)
                alerts.append(alert)
                logger.info(f"🔔 Device Offline Alert: {device.ip_address}")
        
        if alerts:
            db.session.commit()
        
        return alerts
    
    def check_device_online(self, device):
        """
        Check if a previously offline device is back online
        
        Args:
            device: Device object
            
        Returns:
            Alert object or None
        """
        if device.status == 'OFFLINE':
            # Check if there's an unacknowledged offline alert
            offline_alert = Alert.query.filter_by(
                device_id=device.id,
                alert_type=self.ALERT_DEVICE_OFFLINE,
                acknowledged=False
            ).first()
            
            if offline_alert:
                # Device is back online
                device.status = 'ONLINE'
                alert = Alert(
                    alert_type=self.ALERT_DEVICE_ONLINE,
                    device_id=device.id,
                    description=f"Device is back online: {device.ip_address} ({device.hostname or 'Unknown'})",
                    severity=self.SEVERITY_LOW,
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(alert)
                db.session.commit()
                logger.info(f"🔔 Device Online Alert: {device.ip_address}")
                return alert
        
        return None
    
    def process_devices(self, devices_data):
        """
        Process discovered devices and generate alerts
        
        Args:
            devices_data: List of device data from agent
            
        Returns:
            dict: Alert statistics
        """
        alerts_generated = {
            'new_device': 0,
            'new_open_port': 0,
            'device_offline': 0,
            'device_online': 0
        }
        
        for device_data in devices_data:
            ip = device_data.get('ip_address')
            if not ip:
                continue
            
            device = Device.query.filter_by(ip_address=ip).first()
            
            if not device:
                # New device - will be created by ingestion
                continue
            
            # Check if device is back online
            online_alert = self.check_device_online(device)
            if online_alert:
                alerts_generated['device_online'] += 1
            
            # Check for new device (if just created)
            new_device_alert = self.check_new_device(device)
            if new_device_alert:
                alerts_generated['new_device'] += 1
            
            # Check for new open ports (from port scans)
            if device_data.get('port_scans'):
                new_port_alerts = self.check_new_open_port(device, device_data['port_scans'])
                alerts_generated['new_open_port'] += len(new_port_alerts)
        
        # Check for offline devices
        offline_alerts = self.check_device_offline()
        alerts_generated['device_offline'] += len(offline_alerts)
        
        return alerts_generated
    
    def get_unacknowledged_count(self):
        """Get count of unacknowledged alerts"""
        return Alert.query.filter_by(acknowledged=False).count()
    
    def get_alerts_by_severity(self):
        """Get count of alerts by severity"""
        low = Alert.query.filter_by(severity=self.SEVERITY_LOW, acknowledged=False).count()
        medium = Alert.query.filter_by(severity=self.SEVERITY_MEDIUM, acknowledged=False).count()
        high = Alert.query.filter_by(severity=self.SEVERITY_HIGH, acknowledged=False).count()
        return {'low': low, 'medium': medium, 'high': high}
