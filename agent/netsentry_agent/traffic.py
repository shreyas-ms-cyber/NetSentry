"""
Traffic Telemetry - Network traffic monitoring with psutil and Scapy
"""

import logging
import time
import psutil
from datetime import datetime, timezone
from collections import defaultdict
import threading

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logging.getLogger(__name__).warning("Scapy not available - packet capture will be limited")

from netsentry_agent.config import AgentConfig

logger = logging.getLogger(__name__)

class TrafficMonitor:
    """Network traffic monitoring using psutil and packet capture"""
    
    def __init__(self, interface=None):
        """
        Initialize traffic monitor
        
        Args:
            interface: Network interface to monitor (auto-detects if None)
        """
        self.interface = interface or AgentConfig.NETWORK_INTERFACE
        self.packet_counts = {
            'tcp': 0,
            'udp': 0,
            'icmp': 0,
            'other': 0
        }
        self.total_packets = 0
        self.start_time = None
        self.last_sample_time = None
        self.baseline_stats = None
        self.packets_per_sec = 0
        self.bandwidth_bytes = 0
        self.talkers = defaultdict(lambda: {'bytes': 0, 'packets': 0})
        self.running = False
        self.sniffer_thread = None
        self.lock = threading.Lock()
        self.packet_count_since_last_sample = 0
        self.byte_count_since_last_sample = 0
        self.last_packet_count = 0
        self.last_byte_count = 0
    
    def get_interface_stats(self):
        """Get network interface statistics using psutil"""
        try:
            stats = psutil.net_io_counters(pernic=True)
            if self.interface in stats:
                iface_stats = stats[self.interface]
                return {
                    'bytes_sent': iface_stats.bytes_sent,
                    'bytes_recv': iface_stats.bytes_recv,
                    'packets_sent': iface_stats.packets_sent,
                    'packets_recv': iface_stats.packets_recv,
                    'errin': iface_stats.errin,
                    'errout': iface_stats.errout,
                    'dropin': iface_stats.dropin,
                    'dropout': iface_stats.dropout
                }
            else:
                # Try to find the first active interface
                for name, stats in stats.items():
                    if stats.bytes_recv > 0 or stats.bytes_sent > 0:
                        logger.info(f"Using interface: {name}")
                        self.interface = name
                        return {
                            'bytes_sent': stats.bytes_sent,
                            'bytes_recv': stats.bytes_recv,
                            'packets_sent': stats.packets_sent,
                            'packets_recv': stats.packets_recv,
                            'errin': stats.errin,
                            'errout': stats.errout,
                            'dropin': stats.dropin,
                            'dropout': stats.dropout
                        }
                logger.warning("No active network interface found")
                return None
        except Exception as e:
            logger.error(f"Error getting interface stats: {e}")
            return None
    
    def calculate_traffic(self):
        """Calculate traffic rates from interface statistics"""
        current_stats = self.get_interface_stats()
        
        if not current_stats:
            return None
        
        if not self.baseline_stats:
            self.baseline_stats = current_stats
            self.last_sample_time = datetime.now(timezone.utc)
            self.last_packet_count = 0
            self.last_byte_count = 0
            return None
        
        # Calculate time difference
        now = datetime.now(timezone.utc)
        time_diff = (now - self.last_sample_time).total_seconds()
        
        if time_diff <= 0:
            return None
        
        # Calculate rates
        bytes_sent = current_stats['bytes_sent'] - self.baseline_stats['bytes_sent']
        bytes_recv = current_stats['bytes_recv'] - self.baseline_stats['bytes_recv']
        packets_sent = current_stats['packets_sent'] - self.baseline_stats['packets_sent']
        packets_recv = current_stats['packets_recv'] - self.baseline_stats['packets_recv']
        
        # Calculate per-second rates
        total_bytes = bytes_sent + bytes_recv
        total_packets = packets_sent + packets_recv
        
        self.packets_per_sec = total_packets / time_diff if time_diff > 0 else 0
        self.bandwidth_bytes = total_bytes / time_diff if time_diff > 0 else 0
        
        # Update baseline
        self.baseline_stats = current_stats
        self.last_sample_time = now
        
        return {
            'packets_per_sec': self.packets_per_sec,
            'bandwidth_bytes': self.bandwidth_bytes,
            'bandwidth_mbps': round((self.bandwidth_bytes * 8) / 1000000, 2),
            'total_packets': total_packets,
            'total_bytes': total_bytes,
            'time_diff': time_diff
        }
    
    def packet_callback(self, packet):
        """Callback for packet capture - counts packets and updates stats"""
        try:
            if packet.haslayer(IP):
                ip = packet[IP]
                src = ip.src
                dst = ip.dst
                size = len(packet)
                
                # Determine protocol
                if packet.haslayer(TCP):
                    protocol = 'tcp'
                elif packet.haslayer(UDP):
                    protocol = 'udp'
                elif packet.haslayer(ICMP):
                    protocol = 'icmp'
                else:
                    protocol = 'other'
                
                with self.lock:
                    # Update packet counts
                    self.packet_counts[protocol] += 1
                    self.total_packets += 1
                    self.packet_count_since_last_sample += 1
                    self.byte_count_since_last_sample += size
                    
                    # Track talkers (both source and destination)
                    self.talkers[src]['bytes'] += size
                    self.talkers[src]['packets'] += 1
                    self.talkers[dst]['bytes'] += size
                    self.talkers[dst]['packets'] += 1
                    
        except Exception as e:
            logger.debug(f"Error processing packet: {e}")
    
    def start_sniffing(self):
        """Start packet capture in background thread"""
        if not SCAPY_AVAILABLE:
            logger.warning("Scapy not available - packet capture disabled")
            return False
        
        if self.running:
            return True
        
        self.running = True
        self.start_time = datetime.now(timezone.utc)
        self.last_sample_time = self.start_time
        self.packet_count_since_last_sample = 0
        self.byte_count_since_last_sample = 0
        
        # Reset stats when starting new capture
        with self.lock:
            self.packet_counts = {
                'tcp': 0,
                'udp': 0,
                'icmp': 0,
                'other': 0
            }
            self.total_packets = 0
            self.talkers = defaultdict(lambda: {'bytes': 0, 'packets': 0})
        
        def sniff_thread():
            try:
                logger.info(f"📡 Starting packet capture on interface: {self.interface}")
                sniff(
                    iface=self.interface,
                    prn=self.packet_callback,
                    store=False,
                    stop_filter=lambda _: not self.running
                )
            except Exception as e:
                logger.error(f"Error in packet capture: {e}")
                self.running = False
        
        self.sniffer_thread = threading.Thread(target=sniff_thread, daemon=True)
        self.sniffer_thread.start()
        return True
    
    def stop_sniffing(self):
        """Stop packet capture"""
        self.running = False
        if self.sniffer_thread:
            self.sniffer_thread.join(timeout=2)
        logger.info("📡 Packet capture stopped")
    
    def get_traffic_stats(self):
        """Get current traffic statistics"""
        with self.lock:
            # Calculate protocol distribution percentages
            total = sum(self.packet_counts.values())
            protocol_breakdown = {}
            
            if total > 0:
                for proto, count in self.packet_counts.items():
                    protocol_breakdown[proto] = round((count / total) * 100, 1)
            else:
                protocol_breakdown = {
                    'tcp': 0,
                    'udp': 0,
                    'icmp': 0,
                    'other': 0
                }
            
            # Get top talkers (limit to top 10)
            top_talkers = sorted(
                self.talkers.items(),
                key=lambda x: x[1]['bytes'],
                reverse=True
            )[:10]
            
            top_talkers_list = [
                {
                    'ip': ip,
                    'bytes': data['bytes'],
                    'packets': data['packets'],
                    'bytes_mb': round(data['bytes'] / 1024 / 1024, 2)
                }
                for ip, data in top_talkers
            ]
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'packets_per_sec': round(self.packets_per_sec, 2),
                'bandwidth_bytes': round(self.bandwidth_bytes, 2),
                'bandwidth_mbps': round((self.bandwidth_bytes * 8) / 1000000, 2),
                'total_packets': self.total_packets,
                'protocol_breakdown': protocol_breakdown,
                'packet_counts': self.packet_counts.copy(),
                'top_talkers': top_talkers_list
            }
    
    def get_protocol_breakdown(self):
        """Get protocol breakdown percentages"""
        total = sum(self.packet_counts.values())
        if total == 0:
            return {'tcp': 0, 'udp': 0, 'icmp': 0, 'other': 0}
        
        return {
            'tcp': round((self.packet_counts['tcp'] / total) * 100, 1),
            'udp': round((self.packet_counts['udp'] / total) * 100, 1),
            'icmp': round((self.packet_counts['icmp'] / total) * 100, 1),
            'other': round((self.packet_counts['other'] / total) * 100, 1)
        }
    
    def reset_stats(self):
        """Reset all traffic statistics"""
        with self.lock:
            self.packet_counts = {
                'tcp': 0,
                'udp': 0,
                'icmp': 0,
                'other': 0
            }
            self.total_packets = 0
            self.talkers = defaultdict(lambda: {'bytes': 0, 'packets': 0})
            self.packets_per_sec = 0
            self.bandwidth_bytes = 0
            self.baseline_stats = None
            self.last_sample_time = None

def test_traffic_monitor():
    """Test function for traffic monitor"""
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "=" * 60)
    print("Testing Traffic Monitor")
    print("=" * 60 + "\n")
    
    monitor = TrafficMonitor()
    
    # Get interface stats
    stats = monitor.get_interface_stats()
    if stats:
        print("Interface Statistics:")
        print(f"  Interface: {monitor.interface}")
        print(f"  Bytes Sent: {stats['bytes_sent']:,}")
        print(f"  Bytes Recv: {stats['bytes_recv']:,}")
    
    # Start packet capture
    print("\nStarting packet capture (20 seconds)...")
    monitor.start_sniffing()
    
    # Monitor traffic
    for i in range(20):
        time.sleep(1)
        result = monitor.calculate_traffic()
        if result and i % 5 == 0:
            print(f"  {i+1}s: {result['packets_per_sec']:.1f} pps, {result['bandwidth_mbps']:.2f} Mbps")
    
    # Stop capture
    monitor.stop_sniffing()
    
    # Get stats
    stats = monitor.get_traffic_stats()
    print("\n" + "=" * 60)
    print("Traffic Statistics")
    print("=" * 60)
    print(f"  Total Packets: {stats['total_packets']}")
    print(f"  Packets/sec: {stats['packets_per_sec']}")
    print(f"  Bandwidth: {stats['bandwidth_mbps']} Mbps")
    print(f"  Protocol Breakdown: {stats['protocol_breakdown']}")
    print(f"  Packet Counts: {stats['packet_counts']}")
    
    if stats['top_talkers']:
        print("\n  Top Talkers:")
        for talker in stats['top_talkers'][:5]:
            print(f"    {talker['ip']}: {talker['bytes_mb']:.2f} MB ({talker['packets']} packets)")
    
    print("=" * 60)

if __name__ == '__main__':
    test_traffic_monitor()
