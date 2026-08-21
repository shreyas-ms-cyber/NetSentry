"""
Unit tests for MAC Vendor Lookup
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from netsentry_agent.vendor import MACVendorLookup

class TestMACVendorLookup:
    """Tests for MAC vendor lookup"""
    
    def test_lookup_vendor_known(self):
        # Test known vendors
        assert MACVendorLookup.lookup_vendor('00:0C:29:AA:BB:CC') == 'VMware'
        assert MACVendorLookup.lookup_vendor('00:50:56:AA:BB:CC') == 'VMware'
        assert MACVendorLookup.lookup_vendor('00:15:5D:AA:BB:CC') == 'Microsoft'
        assert MACVendorLookup.lookup_vendor('00:1A:2B:AA:BB:CC') == 'Netgear'
    
    def test_lookup_vendor_unknown(self):
        assert MACVendorLookup.lookup_vendor('00:00:00:00:00:00') == 'Unknown Vendor'
        assert MACVendorLookup.lookup_vendor('FF:FF:FF:FF:FF:FF') == 'Unknown Vendor'
    
    def test_lookup_vendor_case_insensitive(self):
        assert MACVendorLookup.lookup_vendor('00:0c:29:aa:bb:cc') == 'VMware'
        assert MACVendorLookup.lookup_vendor('00:15:5d:aa:bb:cc') == 'Microsoft'
    
    def test_lookup_vendor_empty(self):
        assert MACVendorLookup.lookup_vendor('') == 'Unknown Vendor'
        assert MACVendorLookup.lookup_vendor(None) == 'Unknown Vendor'
    
    def test_lookup_vendor_invalid(self):
        assert MACVendorLookup.lookup_vendor('invalid') == 'Unknown Vendor'
        assert MACVendorLookup.lookup_vendor('12:34') == 'Unknown Vendor'
