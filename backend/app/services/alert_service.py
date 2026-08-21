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
    
    ALERT_NEW_DEVICE = 'NEW_DEVICE'
    ALERT_NEW_OPEN_PORT = 'NEW_OPEN_PORT'
    ALERT_DEVICE_OFFLINE = 'DEVICE_OFFLINE'
    ALERT_DEVICE_ONLINE = 'DEVICE_ONLINE'
    
    SEVERITY_LOW = 'LOW'
    SEVERITY_MEDIUM = 'MEDIUM'
    SEVERITY_HIGH = 'HIGH'
    
    def __init__(self):
        self.offline_threshold_minutes = 5
    
    def check_new_device(self, device):
        """Check if this is a new device and generate alert"""
        if device.first_seen:
            # Make sure both datetimes are timezone-aware
            now = datetime.now(timezone.utc)
            first_seen = device.first_seen
            if first_seen.tzinfo is None:
                first_seen = first_seen.replace(tzinfo=timezone.utc)
            time_since_creation = now - first_seen
            if time_since_creation.total_seconds() < 120:
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
    
    # ... rest of the methods remain the same ...
