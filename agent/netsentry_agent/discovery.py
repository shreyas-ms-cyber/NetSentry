"""
Device Discovery - ARP-based device discovery on local network
"""

import logging
import socket
import time
from datetime import datetime

try:
    from scapy.all import ARP, Ether, srp, conf
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logging.getLogger(__name__).warning("Scapy not available - discovery will be limited")

from netsentry_agent.network_scope import NetworkScopeValidator
from netsentry_agent.vendor import MACVendorLookup
from netsentry_agent.config import AgentConfig

logger = logging.getLogger(__name__)

class DeviceDiscovery:
    """Network device discovery using ARP scanning"""
    
    def __init__(self):
        self.devices = []
        self.scan_time = None
        self.network_info = None
    
    def discover_network(self):
        """Discover the local network configuration"""
        network_info = NetworkScopeValidator.get_active_private_network()
        
        if not network_info:
            logger.error("No active private network found!")
            return None
        
        logger.info(f"📡 Found network: {network_info['network']}")
        logger.info(f"🌐 Interface: {network_info['name']}")
        logger.info(f"📱 Local IP: {network_info['ip']}")
        logger.info(f"🔢 Netmask: {network_info['netmask']}")
        
        self.network_info = network_info
        return network_info
    
    def scan_network(self, network_cidr=None):
        """
        Perform ARP scan to discover devices on the network
        
        Args:
            network_cidr: Optional network CIDR to scan (e.g., '192.168.1.0/24')
                         If not provided, auto-detects from network interface
        """
        if not SCAPY_AVAILABLE:
            logger.error("Scapy not installed. Cannot perform ARP discovery.")
            logger.error("Install scapy: pip install scapy")
            return []
        
        # Get network information
        if not self.network_info:
            self.discover_network()
        
        if not self.network_info:
            logger.error("Could not discover network configuration")
            return []
        
        # Use provided network or auto-detected
        if network_cidr:
            target_network = network_cidr
        else:
            target_network = self.network_info['network']
        
        # Validate network is private
        if not NetworkScopeValidator.validate_network(target_network):
            logger.error(f"Network {target_network} is not a valid private network")
            return []
        
        logger.info(f"🔍 Scanning network: {target_network}")
        
        # Create ARP request
        arp = ARP(pdst=target_network)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp
        
        try:
            # Send ARP request and receive responses
            logger.info(f"📤 Sending ARP requests to {target_network}...")
            result = srp(
                packet,
                timeout=AgentConfig.DISCOVERY_TIMEOUT,
                verbose=False,
                retry=2
            )[0]
            
            self.devices = []
            self.scan_time = datetime.utcnow()
            
            # Process responses
            for sent, received in result:
                try:
                    ip = received.psrc
                    mac = received.hwsrc
                    
                    # Validate IP is private
                    if not NetworkScopeValidator.validate_target(ip):
                        logger.debug(f"Skipping non-private IP: {ip}")
                        continue
                    
                    # Look up vendor
                    vendor = MACVendorLookup.lookup_vendor(mac)
                    
                    # Try to resolve hostname
                    hostname = self._resolve_hostname(ip)
                    
                    device = {
                        'ip_address': ip,
                        'mac_address': mac,
                        'vendor': vendor,
                        'hostname': hostname,
                        'status': 'ONLINE',
                        'first_seen': self.scan_time.isoformat(),
                        'last_seen': self.scan_time.isoformat()
                    }
                    
                    self.devices.append(device)
                    logger.info(f"✅ Found device: {ip} ({mac}) - {vendor} - {hostname or 'No hostname'}")
                    
                except Exception as e:
                    logger.debug(f"Error processing device: {e}")
                    continue
            
            logger.info(f"📊 Discovery complete. Found {len(self.devices)} devices.")
            return self.devices
            
        except Exception as e:
            logger.error(f"Error during ARP scan: {e}")
            return []
    
    def _resolve_hostname(self, ip):
        """Attempt to resolve hostname from IP address"""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except socket.herror:
            return None
        except Exception:
            return None
    
    def get_devices(self):
        """Get list of discovered devices"""
        return self.devices
    
    def get_device_count(self):
        """Get number of discovered devices"""
        return len(self.devices)
    
    def get_summary(self):
        """Get summary of discovery results"""
        return {
            'total_devices': len(self.devices),
            'network': self.network_info['network'] if self.network_info else None,
            'scan_time': self.scan_time.isoformat() if self.scan_time else None,
            'devices': self.devices
        }

def test_discovery():
    """Test function to run discovery"""
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "=" * 60)
    print("Testing Device Discovery")
    print("=" * 60 + "\n")
    
    discovery = DeviceDiscovery()
    
    # Discover network
    network = discovery.discover_network()
    if not network:
        print("❌ No network found!")
        return
    
    # Scan network
    devices = discovery.scan_network()
    
    print("\n" + "=" * 60)
    print("Discovery Results")
    print("=" * 60)
    print(f"Network: {discovery.network_info['network']}")
    print(f"Total Devices Found: {len(devices)}")
    print("\nDevice List:")
    print("-" * 60)
    
    for device in devices:
        print(f"  📱 {device['ip_address']}")
        print(f"     MAC: {device['mac_address']}")
        print(f"     Vendor: {device['vendor']}")
        print(f"     Hostname: {device['hostname'] or 'N/A'}")
        print()
    
    print("=" * 60)

if __name__ == '__main__':
    test_discovery()
