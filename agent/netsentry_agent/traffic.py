"""
Traffic Telemetry - Network traffic monitoring
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
    logging.getLogger(__name__).warning("Scapy not available")

from netsentry_agent.config import AgentConfig

logger = logging.getLogger(__name__)

class TrafficMonitor:
    def __init__(self, interface=None):
        self.interface = interface or AgentConfig.NETWORK_INTERFACE
        self.packet_counts = {'tcp': 0, 'udp': 0, 'icmp': 0, 'other': 0}
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

    def get_interface_stats(self):
        try:
            stats = psutil.net_io_counters(pernic=True)
            if self.interface in stats:
                iface_stats = stats[self.interface]
                return {
                    'bytes_sent': iface_stats.bytes_sent,
                    'bytes_recv': iface_stats.bytes_recv,
                    'packets_sent': iface_stats.packets_sent,
                    'packets_recv': iface_stats.packets_recv,
                }
            else:
                for name, stats in stats.items():
                    if stats.bytes_recv > 0 or stats.bytes_sent > 0:
                        self.interface = name
                        return {
                            'bytes_sent': stats.bytes_sent,
                            'bytes_recv': stats.bytes_recv,
                            'packets_sent': stats.packets_sent,
                            'packets_recv': stats.packets_recv,
                        }
                return None
        except Exception as e:
            logger.error(f"Error getting interface stats: {e}")
            return None

    def calculate_traffic(self):
        current_stats = self.get_interface_stats()
        if not current_stats:
            return None
        
        if not self.baseline_stats:
            self.baseline_stats = current_stats
            self.last_sample_time = datetime.now(timezone.utc)
            return None
        
        now = datetime.now(timezone.utc)
        time_diff = (now - self.last_sample_time).total_seconds()
        if time_diff <= 0:
            return None
        
        bytes_sent = current_stats['bytes_sent'] - self.baseline_stats['bytes_sent']
        bytes_recv = current_stats['bytes_recv'] - self.baseline_stats['bytes_recv']
        packets_sent = current_stats['packets_sent'] - self.baseline_stats['packets_sent']
        packets_recv = current_stats['packets_recv'] - self.baseline_stats['packets_recv']
        
        total_bytes = bytes_sent + bytes_recv
        total_packets = packets_sent + packets_recv
        
        self.packets_per_sec = total_packets / time_diff if time_diff > 0 else 0
        self.bandwidth_bytes = total_bytes / time_diff if time_diff > 0 else 0
        
        self.baseline_stats = current_stats
        self.last_sample_time = now
        
        return {
            'packets_per_sec': self.packets_per_sec,
            'bandwidth_bytes': self.bandwidth_bytes,
            'bandwidth_mbps': round((self.bandwidth_bytes * 8) / 1000000, 2)
        }

    def packet_callback(self, packet):
        try:
            if packet.haslayer(IP):
                ip = packet[IP]
                src = ip.src
                dst = ip.dst
                size = len(packet)
                
                if packet.haslayer(TCP):
                    protocol = 'tcp'
                elif packet.haslayer(UDP):
                    protocol = 'udp'
                elif packet.haslayer(ICMP):
                    protocol = 'icmp'
                else:
                    protocol = 'other'
                
                with self.lock:
                    self.packet_counts[protocol] += 1
                    self.total_packets += 1
                    self.talkers[src]['bytes'] += size
                    self.talkers[src]['packets'] += 1
                    self.talkers[dst]['bytes'] += size
                    self.talkers[dst]['packets'] += 1
        except Exception as e:
            logger.debug(f"Error processing packet: {e}")

    def start_sniffing(self):
        if not SCAPY_AVAILABLE:
            logger.warning("Scapy not available - packet capture disabled")
            return False
        
        if self.running:
            return True
        
        self.running = True
        self.start_time = datetime.now(timezone.utc)
        self.last_sample_time = self.start_time
        
        with self.lock:
            self.packet_counts = {'tcp': 0, 'udp': 0, 'icmp': 0, 'other': 0}
            self.total_packets = 0
            self.talkers = defaultdict(lambda: {'bytes': 0, 'packets': 0})
        
        def sniff_thread():
            try:
                logger.info(f"📡 Starting packet capture on: {self.interface}")
                sniff(
                    iface=self.interface,
                    prn=self.packet_callback,
                    store=False,
                    stop_filter=lambda _: not self.running
                )
            except Exception as e:
                logger.error(f"Packet capture error: {e}")
                self.running = False
        
        self.sniffer_thread = threading.Thread(target=sniff_thread, daemon=True)
        self.sniffer_thread.start()
        return True

    def stop_sniffing(self):
        self.running = False
        if self.sniffer_thread:
            self.sniffer_thread.join(timeout=2)
        logger.info("📡 Packet capture stopped")

    def get_traffic_stats(self):
        with self.lock:
            total = sum(self.packet_counts.values())
            protocol_breakdown = {}
            if total > 0:
                for proto, count in self.packet_counts.items():
                    protocol_breakdown[proto] = round((count / total) * 100, 1)
            else:
                protocol_breakdown = {'tcp': 0, 'udp': 0, 'icmp': 0, 'other': 0}
            
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
                'top_talkers': top_talkers_list
            }
