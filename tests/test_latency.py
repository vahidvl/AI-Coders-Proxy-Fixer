import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from proxy_core import ProxyManagerCore

class TestLatencyTester(unittest.TestCase):
    def setUp(self):
        self.core = ProxyManagerCore(proxy_address="127.0.0.1", proxy_port="10808")

    def test_api_latency(self):
        results = self.core.test_api_latency()
        self.assertIsInstance(results, dict)
        self.assertIn("Google", results)
        self.assertIn("Claude API", results)
        self.assertIn("Cloud Code API", results)

if __name__ == '__main__':
    unittest.main()
