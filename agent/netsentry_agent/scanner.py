"""
Port Scanner - TCP socket-based port scanning
"""

import socket
import logging
import threading
import time
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class PortScanner:
    """TCP port scanner for network devices"""
    
    # Common ports and their services
    COMMON_PORTS = {
        21: 'FTP',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        143: 'IMAP',
        443: 'HTTPS',
        445: 'SMB',
        465: 'SMTPS',
        587: 'SMTP-Submit',
        993: 'IMAPS',
        995: 'POP3S',
        1433: 'MSSQL',
        3306: 'MySQL',
        3389: 'RDP',
        5432: 'PostgreSQL',
        6379: 'Redis',
        8080: 'HTTP-Alt',
        8443: 'HTTPS-Alt',
        9200: 'Elasticsearch',
        27017: 'MongoDB'
    }
    
    def __init__(self, timeout=1.0, max_workers=50):
        """
        Initialize port scanner
        
        Args:
            timeout: Connection timeout in seconds
            max_workers: Maximum concurrent scan threads
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = []
        self.scan_time = None
        self.target_ip = None
    
    def scan_port(self, ip, port, protocol='TCP'):
        """
        Scan a single port on a target IP
        
        Args:
            ip: Target IP address
            port: Port number to scan
            protocol: Protocol (TCP only for now)
            
        Returns:
            dict: Port scan result or None if failed
        """
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Attempt connection
            start_time = time.time()
            result = sock.connect_ex((ip, port))
            end_time = time.time()
            
            # Close socket
            sock.close()
            
            # Determine status
            if result == 0:
                status = 'OPEN'
            elif result == 111 or result == 10061:  # Connection refused
                status = 'CLOSED'
            else:
                status = 'FILTERED'
            
            # Get service name if available
            service = self.COMMON_PORTS.get(port)
            
            return {
                'port': port,
                'protocol': protocol,
                'status': status,
                'service': service,
                'response_time_ms': round((end_time - start_time) * 1000, 2),
                'device_ip': ip  # Add device_ip for backend lookup
            }
            
        except socket.error as e:
            logger.debug(f"Socket error on {ip}:{port} - {e}")
            return None
        except Exception as e:
            logger.debug(f"Error scanning {ip}:{port} - {e}")
            return None
    
    def scan_ports(self, ip, ports=None):
        """
        Scan multiple ports on a target IP
        
        Args:
            ip: Target IP address
            ports: List of ports to scan (uses COMMON_PORTS if None)
            
        Returns:
            list: List of port scan results
        """
        if ports is None:
            ports = list(self.COMMON_PORTS.keys())
        
        self.target_ip = ip
        logger.info(f"🔍 Scanning {len(ports)} ports on {ip}...")
        
        self.results = []
        self.scan_time = datetime.now(timezone.utc)
        
        # Use ThreadPoolExecutor for concurrent scanning
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scan tasks
            future_to_port = {
                executor.submit(self.scan_port, ip, port): port 
                for port in ports
            }
            
            # Collect results
            for future in as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result()
                    if result:
                        self.results.append(result)
                        if result['status'] == 'OPEN':
                            service = result.get('service', 'Unknown')
                            logger.info(f"  ✅ Port {port}/{result['protocol']} OPEN - {service}")
                except Exception as e:
                    logger.debug(f"Error getting result for port {port}: {e}")
        
        # Sort results by port number
        self.results.sort(key=lambda x: x['port'])
        
        # Count open ports
        open_ports = [r for r in self.results if r['status'] == 'OPEN']
        logger.info(f"📊 Scan complete. Found {len(open_ports)} open ports on {ip}")
        
        return self.results
    
    def scan_device(self, device):
        """
        Scan a device dictionary from discovery
        
        Args:
            device: Device dictionary with 'ip_address' key
            
        Returns:
            dict: Device with port scan results
        """
        ip = device.get('ip_address')
        if not ip:
            logger.error("Device has no IP address")
            return device
        
        # Scan ports
        port_results = self.scan_ports(ip)
        
        # Add device_ip to each result for backend
        for result in port_results:
            result['device_ip'] = ip
        
        # Add results to device
        device['port_scans'] = port_results
        device['open_ports'] = [p for p in port_results if p['status'] == 'OPEN']
        device['scan_time'] = self.scan_time.isoformat() if self.scan_time else None
        
        return device
    
    def get_open_ports(self):
        """Get list of open ports from last scan"""
        return [r for r in self.results if r['status'] == 'OPEN']
    
    def get_summary(self):
        """Get summary of last scan"""
        return {
            'total_scanned': len(self.results),
            'open_ports': len(self.get_open_ports()),
            'scan_time': self.scan_time.isoformat() if self.scan_time else None,
            'results': self.results
        }
    
    def to_dict(self, device_id=None):
        """
        Convert scan results to dict for API ingestion
        
        Args:
            device_id: Optional device ID to associate results with
            
        Returns:
            list: List of port scan dicts for API
        """
        return [
            {
                'device_id': device_id,
                'device_ip': r.get('device_ip'),  # Include device_ip for lookup
                'port': r['port'],
                'protocol': r['protocol'],
                'status': r['status'],
                'service': r.get('service'),
                'scanned_at': self.scan_time.isoformat() if self.scan_time else None
            }
            for r in self.results
        ]

def test_scanner():
    """Test function for port scanner"""
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "=" * 60)
    print("Testing Port Scanner")
    print("=" * 60 + "\n")
    
    # Test IP (localhost or a known device)
    test_ip = '127.0.0.1'  # localhost for testing
    test_ports = [22, 80, 443, 3306, 8080]
    
    print(f"Testing scan on {test_ip} with ports: {test_ports}")
    print("-" * 60)
    
    scanner = PortScanner(timeout=1.0)
    results = scanner.scan_ports(test_ip, test_ports)
    
    print("\n" + "=" * 60)
    print("Scan Results")
    print("=" * 60)
    
    for result in results:
        status_icon = {
            'OPEN': '🟢',
            'CLOSED': '🔴',
            'FILTERED': '🟡'
        }.get(result['status'], '⚪')
        
        service = result.get('service', 'Unknown')
        print(f"  {status_icon} Port {result['port']}/TCP: {result['status']} - {service}")
    
    print("\n" + "=" * 60)
    print(f"Total ports scanned: {len(results)}")
    print(f"Open ports: {len([r for r in results if r['status'] == 'OPEN'])}")
    print("=" * 60)

if __name__ == '__main__':
    test_scanner()
