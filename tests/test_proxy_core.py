import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from proxy_core import ProxyManagerCore

class TestProxyCore(unittest.TestCase):
    def setUp(self):
        self.core = ProxyManagerCore(proxy_address="127.0.0.1", proxy_port="10808")

    def test_proxy_toggle(self):
        success, msg = self.core.enable_proxy()
        self.assertTrue(success, f"Failed to enable: {msg}")
        self.assertTrue(self.core.check_status(), "Status check says proxy is disabled after enabling")

        success, msg = self.core.disable_proxy()
        self.assertTrue(success, f"Failed to disable: {msg}")
        self.assertFalse(self.core.check_status(), "Status check says proxy is enabled after disabling")

    def test_start_with_windows_toggle(self):
        ok, msg = self.core.set_start_with_windows(True)
        self.assertTrue(ok, msg)
        self.assertTrue(self.core.check_start_with_windows())

        ok, msg = self.core.set_start_with_windows(False)
        self.assertTrue(ok, msg)
        self.assertFalse(self.core.check_start_with_windows())

if __name__ == '__main__':
    unittest.main()
