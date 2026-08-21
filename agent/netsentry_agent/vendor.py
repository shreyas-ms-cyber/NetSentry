"""
MAC Vendor Lookup - Identifies device manufacturers from MAC addresses
Uses a local OUI mapping file to avoid external API calls
"""

import os
import logging
import re

logger = logging.getLogger(__name__)

class MACVendorLookup:
    """MAC address vendor lookup using local OUI database"""
    
    # Path to OUI database file
    OUI_FILE = os.path.join(os.path.dirname(__file__), 'oui.txt')
    
    # Cache for vendor lookups
    _vendor_cache = {}
    
    @classmethod
    def _load_oui_database(cls):
        """Load OUI database from file or create minimal built-in database"""
        if cls._vendor_cache:
            return
        
        # Built-in common vendor database
        # In production, you would download the full IEEE OUI database
        builtin_oui = {
            '00:00:0C': 'Cisco',
            '00:01:02': 'Cisco',
            '00:05:5D': 'Cisco',
            '00:0C:29': 'VMware',
            '00:50:56': 'VMware',
            '00:15:5D': 'Microsoft',
            '00:1A:3F': 'Microsoft',
            '00:1B:77': 'Microsoft',
            '00:1C:C0': 'Microsoft',
            '00:1D:D8': 'Microsoft',
            '00:1E:37': 'Microsoft',
            '00:1F:3A': 'Microsoft',
            '00:21:5A': 'Microsoft',
            '00:23:18': 'Microsoft',
            '00:24:8C': 'Microsoft',
            '00:25:AE': 'Microsoft',
            '00:26:5E': 'Microsoft',
            '00:27:0E': 'Microsoft',
            '00:28:F8': 'Microsoft',
            '00:29:7D': 'Microsoft',
            '00:2A:8A': 'Microsoft',
            '00:2B:97': 'Microsoft',
            '00:2C:4A': 'Microsoft',
            '00:2D:5D': 'Microsoft',
            '00:30:48': 'Dell',
            '00:34:56': 'Dell',
            '00:3A:4D': 'Dell',
            '00:40:CA': 'Dell',
            '00:50:6B': 'HP',
            '00:60:08': 'HP',
            '00:70:7A': 'HP',
            '00:80:2D': 'HP',
            '00:90:27': 'HP',
            '00:A0:C9': 'HP',
            '00:B0:D0': 'HP',
            '00:C0:9F': 'HP',
            '00:D0:59': 'HP',
            '00:E0:18': 'HP',
            '00:F0:4C': 'HP',
            '00:14:51': 'Apple',
            '00:16:CB': 'Apple',
            '00:17:F2': 'Apple',
            '00:19:E3': 'Apple',
            '00:1B:63': 'Apple',
            '00:1C:B3': 'Apple',
            '00:1D:4F': 'Apple',
            '00:1E:C2': 'Apple',
            '00:1F:03': 'Apple',
            '00:21:E9': 'Apple',
            '00:23:32': 'Apple',
            '00:24:36': 'Apple',
            '00:25:00': 'Apple',
            '00:26:08': 'Apple',
            '00:26:BB': 'Apple',
            '00:27:63': 'Apple',
            '00:28:37': 'Apple',
            '00:29:95': 'Apple',
            '00:2A:2A': 'Apple',
            '00:2B:58': 'Apple',
            '00:2C:26': 'Apple',
            '00:2D:2D': 'Apple',
            '00:30:6E': 'Apple',
            '00:40:96': 'Apple',
            '00:50:E4': 'Apple',
            '00:60:2F': 'Apple',
            '00:70:CD': 'Apple',
            '00:80:92': 'Apple',
            '00:90:93': 'Apple',
            '00:A0:40': 'Apple',
            '00:B0:4E': 'Apple',
            '00:C0:4F': 'Apple',
            '00:D0:3A': 'Apple',
            '00:E0:4C': 'Apple',
            '00:F0:7F': 'Apple',
            'B8:27:EB': 'Raspberry Pi',
            'E4:5F:01': 'Raspberry Pi',
            'DC:A6:32': 'Raspberry Pi',
            '00:1E:06': 'Samsung',
            '00:23:44': 'Samsung',
            '00:24:54': 'Samsung',
            '00:26:5E': 'Samsung',
            '00:28:82': 'Samsung',
            '00:2A:8A': 'Samsung',
            '00:2C:4A': 'Samsung',
            '00:2D:5D': 'Samsung',
            '00:30:6E': 'Samsung',
            '00:40:96': 'Samsung',
            '00:50:E4': 'Samsung',
            '00:60:2F': 'Samsung',
            '00:70:CD': 'Samsung',
            '00:80:92': 'Samsung',
            '00:90:93': 'Samsung',
            '00:A0:40': 'Samsung',
            '00:B0:4E': 'Samsung',
            '00:C0:4F': 'Samsung',
            '00:D0:3A': 'Samsung',
            '00:E0:4C': 'Samsung',
            '00:F0:7F': 'Samsung',
            'D4:85:64': 'Samsung',
            'B0:26:28': 'Samsung',
            '78:8C:3C': 'Samsung',
            '68:1C:A2': 'Samsung',
            '00:1A:2B': 'Netgear',
            '00:24:B2': 'Netgear',
            '00:26:F2': 'Netgear',
            '00:30:4F': 'Netgear',
            '00:40:3B': 'Netgear',
            '00:50:F1': 'Netgear',
            '00:60:1D': 'Netgear',
            '00:70:A9': 'Netgear',
            '00:80:3F': 'Netgear',
            '00:90:96': 'Netgear',
            '00:A0:AE': 'Netgear',
            '00:B0:6E': 'Netgear',
            '00:C0:3E': 'Netgear',
            '00:D0:4E': 'Netgear',
            '00:E0:98': 'Netgear',
            '00:F0:7E': 'Netgear',
            '00:1F:33': 'TP-Link',
            '00:25:86': 'TP-Link',
            '00:27:19': 'TP-Link',
            '00:28:F8': 'TP-Link',
            '00:29:7D': 'TP-Link',
            '00:2A:8A': 'TP-Link',
            '00:2B:97': 'TP-Link',
            '00:2C:4A': 'TP-Link',
            '00:2D:5D': 'TP-Link',
            '00:30:4F': 'TP-Link',
            '00:40:3B': 'TP-Link',
            '00:50:F1': 'TP-Link',
            '00:60:1D': 'TP-Link',
            '00:70:A9': 'TP-Link',
            '00:80:3F': 'TP-Link',
            '00:90:96': 'TP-Link',
            '00:A0:AE': 'TP-Link',
            '00:B0:6E': 'TP-Link',
            '00:C0:3E': 'TP-Link',
            '00:D0:4E': 'TP-Link',
            '00:E0:98': 'TP-Link',
            '00:F0:7E': 'TP-Link',
            '00:11:22': 'Realtek',
            '00:13:8F': 'Realtek',
            '00:15:AF': 'Realtek',
            '00:17:3F': 'Realtek',
            '00:19:DB': 'Realtek',
            '00:1B:2F': 'Realtek',
            '00:1D:7D': 'Realtek',
            '00:1F:3F': 'Realtek',
            '00:21:5A': 'Realtek',
            '00:23:18': 'Realtek',
            '00:25:AE': 'Realtek',
            '00:27:0E': 'Realtek',
            '00:28:F8': 'Realtek',
            '00:2A:8A': 'Realtek',
            '00:2C:4A': 'Realtek',
            '00:2D:5D': 'Realtek',
            '00:30:4F': 'Realtek',
            '00:40:3B': 'Realtek',
            '00:50:F1': 'Realtek',
            '00:60:1D': 'Realtek',
            '00:70:A9': 'Realtek',
            '00:80:3F': 'Realtek',
            '00:90:96': 'Realtek',
            '00:A0:AE': 'Realtek',
            '00:B0:6E': 'Realtek',
            '00:C0:3E': 'Realtek',
            '00:D0:4E': 'Realtek',
            '00:E0:98': 'Realtek',
            '00:F0:7E': 'Realtek',
        }
        
        cls._vendor_cache = builtin_oui
        
        # Try to load custom OUI file if it exists
        if os.path.exists(cls.OUI_FILE):
            try:
                with open(cls.OUI_FILE, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('\t')
                            if len(parts) >= 2:
                                oui = parts[0].strip().upper()
                                vendor = parts[1].strip()
                                cls._vendor_cache[oui] = vendor
                logger.info(f"Loaded {len(cls._vendor_cache)} OUI entries from file")
            except Exception as e:
                logger.warning(f"Error loading OUI file: {e}")
        
        logger.info(f"Using {len(cls._vendor_cache)} built-in OUI entries")
    
    @classmethod
    def lookup_vendor(cls, mac_address):
        """Look up vendor from MAC address"""
        if not mac_address:
            return "Unknown Vendor"
        
        # Clean and normalize MAC address
        mac = mac_address.upper().strip()
        mac = re.sub(r'[^A-F0-9]', '', mac)
        
        # Need at least 6 characters for OUI
        if len(mac) < 6:
            return "Unknown Vendor"
        
        # Get the OUI (first 6 characters)
        oui = mac[:6]
        
        # Format OUI as XX:XX:XX for lookup
        oui_formatted = ':'.join([oui[i:i+2] for i in range(0, 6, 2)])
        
        # Load OUI database if not loaded
        if not cls._vendor_cache:
            cls._load_oui_database()
        
        # Try to find vendor
        vendor = cls._vendor_cache.get(oui_formatted)
        if vendor:
            return vendor
        
        # Try with different formats
        for key in cls._vendor_cache:
            if key.replace(':', '') == oui:
                return cls._vendor_cache[key]
        
        return "Unknown Vendor"
    
    @classmethod
    def add_custom_oui(cls, oui, vendor):
        """Add custom OUI mapping"""
        if len(oui) == 6:
            oui_formatted = ':'.join([oui[i:i+2] for i in range(0, 6, 2)])
            cls._vendor_cache[oui_formatted] = vendor
        elif len(oui) == 17:  # Full MAC address
            oui_formatted = oui[:8]  # First 8 chars = XX:XX:XX
            cls._vendor_cache[oui_formatted] = vendor
        else:
            cls._vendor_cache[oui] = vendor
