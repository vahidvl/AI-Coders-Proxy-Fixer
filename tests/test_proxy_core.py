import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from proxy_core import ProxyManagerCore

class TestProxyCore(unittest.TestCase):
    def setUp(self):
        self.core = ProxyManagerCore(proxy_address="127.0.0.1", proxy_port="10808")
        
    def test_proxy_toggle(self):
        # Test enabling
        success, msg = self.core.enable_proxy()
        self.assertTrue(success, f"Failed to enable: {msg}")
        self.assertTrue(self.core.check_status(), "Status check says proxy is disabled after enabling")
        
        # Test disabling
        success, msg = self.core.disable_proxy()
        self.assertTrue(success, f"Failed to disable: {msg}")
        self.assertFalse(self.core.check_status(), "Status check says proxy is enabled after disabling")

if __name__ == '__main__':
    unittest.main()
