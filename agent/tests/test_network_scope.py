"""
Unit tests for Network Scope Validator
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from netsentry_agent.network_scope import NetworkScopeValidator

class TestNetworkScopeValidator:
    """Tests for network scope validation"""
    
    def test_is_private_ip_true(self):
        assert NetworkScopeValidator.is_private_ip('192.168.1.1') == True
        assert NetworkScopeValidator.is_private_ip('10.0.0.1') == True
        assert NetworkScopeValidator.is_private_ip('172.16.0.1') == True
    
    def test_is_private_ip_false(self):
        assert NetworkScopeValidator.is_private_ip('8.8.8.8') == False
        assert NetworkScopeValidator.is_private_ip('1.1.1.1') == False
        assert NetworkScopeValidator.is_private_ip('127.0.0.1') == False
    
    def test_is_private_network_true(self):
        assert NetworkScopeValidator.is_private_network('192.168.1.0/24') == True
        assert NetworkScopeValidator.is_private_network('10.0.0.0/8') == True
    
    def test_is_private_network_false(self):
        assert NetworkScopeValidator.is_private_network('8.8.8.0/24') == False
        assert NetworkScopeValidator.is_private_network('1.1.1.0/24') == False
    
    def test_validate_target(self):
        assert NetworkScopeValidator.validate_target('192.168.1.1') == True
        assert NetworkScopeValidator.validate_target('8.8.8.8') == False
    
    def test_validate_network(self):
        assert NetworkScopeValidator.validate_network('192.168.1.0/24') == True
        assert NetworkScopeValidator.validate_network('8.8.8.0/24') == False
