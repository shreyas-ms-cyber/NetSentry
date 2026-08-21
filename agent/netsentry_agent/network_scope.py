"""
Network Scope Validation - Ensures all scanning is restricted to private networks
Only RFC1918 private IPv4 ranges are allowed:
- 10.0.0.0/8
- 172.16.0.0/12
- 192.168.0.0/16
"""

import ipaddress
import logging
import socket
import psutil

logger = logging.getLogger(__name__)

class NetworkScopeValidator:
    """Validator to ensure scanning only occurs on private networks"""
    
    # RFC1918 private IPv4 ranges
    PRIVATE_RANGES = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16'),
    ]
    
    @classmethod
    def is_private_ip(cls, ip_str):
        """Check if an IP address is in a private RFC1918 range"""
        try:
            ip = ipaddress.ip_address(ip_str)
            
            # Only support IPv4
            if not isinstance(ip, ipaddress.IPv4Address):
                return False
            
            # Check if in any private range
            for private_range in cls.PRIVATE_RANGES:
                if ip in private_range:
                    return True
            
            return False
            
        except ValueError:
            logger.error(f"Invalid IP address: {ip_str}")
            return False
    
    @classmethod
    def is_private_network(cls, network_str):
        """Check if a network is in a private RFC1918 range"""
        try:
            network = ipaddress.ip_network(network_str, strict=False)
            
            # Only support IPv4
            if not isinstance(network, ipaddress.IPv4Network):
                return False
            
            # Check if network is within any private range
            for private_range in cls.PRIVATE_RANGES:
                if network.subnet_of(private_range):
                    return True
            
            return False
            
        except ValueError:
            logger.error(f"Invalid network: {network_str}")
            return False
    
    @classmethod
    def get_local_interface_info(cls):
        """Get active network interface and subnet information"""
        try:
            interfaces = []
            
            for iface_name, iface_addrs in psutil.net_if_addrs().items():
                # Skip loopback interfaces
                if iface_name == 'lo' or iface_name.startswith('lo'):
                    continue
                
                for addr in iface_addrs:
                    # Only look for IPv4 addresses
                    if addr.family == socket.AF_INET:
                        # Get netmask
                        netmask = addr.netmask
                        if netmask:
                            # Calculate network
                            try:
                                ip = ipaddress.IPv4Address(addr.address)
                                netmask_ip = ipaddress.IPv4Address(netmask)
                                
                                # Calculate network address
                                network = ipaddress.IPv4Network(
                                    f"{addr.address}/{netmask}", strict=False
                                )
                                
                                # Check if it's a private network
                                if cls.is_private_ip(addr.address):
                                    interfaces.append({
                                        'name': iface_name,
                                        'ip': addr.address,
                                        'netmask': netmask,
                                        'network': str(network),
                                        'is_private': True
                                    })
                            except Exception as e:
                                logger.debug(f"Error processing interface {iface_name}: {e}")
            
            return interfaces
            
        except Exception as e:
            logger.error(f"Error getting interface info: {e}")
            return []
    
    @classmethod
    def get_active_private_network(cls):
        """Get the first active private network"""
        interfaces = cls.get_local_interface_info()
        
        for iface in interfaces:
            if iface['is_private']:
                return iface
        
        logger.warning("No active private network found!")
        return None
    
    @classmethod
    def validate_target(cls, target_ip):
        """Validate that a target IP is within allowed private ranges"""
        if not cls.is_private_ip(target_ip):
            logger.warning(f"Target {target_ip} is not in private range - rejecting")
            return False
        return True
    
    @classmethod
    def validate_network(cls, network_str):
        """Validate that a network is within allowed private ranges"""
        if not cls.is_private_network(network_str):
            logger.warning(f"Network {network_str} is not in private range - rejecting")
            return False
        return True
