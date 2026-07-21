import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from scanner import ScannerEngine, scan_proxy_ports, TargetType

class TestScannerEngine(unittest.TestCase):
    def setUp(self):
        self.scanner = ScannerEngine()

    def test_scan_all(self):
        targets = self.scanner.scan_all()
        self.assertIsInstance(targets, list)
        self.assertGreater(len(targets), 0)

        # Check target attributes
        for t in targets:
            self.assertIsNotNone(t.name)
            self.assertIn(t.target_type, [TargetType.IDE, TargetType.SHELL, TargetType.CLI])
            self.assertIsInstance(t.is_installed, bool)
            self.assertIsInstance(t.is_patched, bool)

    def test_scan_proxy_ports(self):
        ports = scan_proxy_ports()
        self.assertIsInstance(ports, list)

if __name__ == '__main__':
    unittest.main()
