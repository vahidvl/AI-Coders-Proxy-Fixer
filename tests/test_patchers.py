import sys
import os
import tempfile
import json
import unittest
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from patchers import TargetPatcher, BLOCK_BEGIN, BLOCK_END

class TestTargetPatcher(unittest.TestCase):
    def setUp(self):
        self.patcher = TargetPatcher(proxy_address="127.0.0.1", proxy_port="10808")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_patch_and_unpatch_ide(self):
        settings_path = self.base_path / "settings.json"
        
        # Patch
        ok, msg = self.patcher.patch_ide(settings_path, is_antigravity=True)
        self.assertTrue(ok, msg)
        self.assertTrue(settings_path.exists())

        data = json.loads(settings_path.read_text(encoding='utf-8'))
        self.assertEqual(data.get('http.proxy'), "http://127.0.0.1:10808")
        self.assertEqual(data.get('http.proxySupport'), 'override')
        self.assertIn("codeiumDev.languageServerEnv", data)

        # Unpatch
        ok, msg = self.patcher.unpatch_ide(settings_path, is_antigravity=True)
        self.assertTrue(ok, msg)

        data = json.loads(settings_path.read_text(encoding='utf-8'))
        self.assertNotIn('http.proxy', data)

    def test_patch_and_unpatch_powershell(self):
        profile_path = self.base_path / "profile.ps1"
        
        ok, msg = self.patcher.patch_powershell(profile_path)
        self.assertTrue(ok, msg)
        
        content = profile_path.read_text(encoding='utf-8')
        self.assertIn(BLOCK_BEGIN, content)
        self.assertIn("$env:HTTP_PROXY", content)

        ok, msg = self.patcher.unpatch_shell(profile_path)
        self.assertTrue(ok, msg)

        content = profile_path.read_text(encoding='utf-8')
        self.assertNotIn(BLOCK_BEGIN, content)

    def test_patch_and_unpatch_bash(self):
        bashrc_path = self.base_path / ".bashrc"

        ok, msg = self.patcher.patch_bash(bashrc_path)
        self.assertTrue(ok, msg)

        content = bashrc_path.read_text(encoding='utf-8')
        self.assertIn(BLOCK_BEGIN, content)
        self.assertIn("export HTTP_PROXY", content)

        ok, msg = self.patcher.unpatch_shell(bashrc_path)
        self.assertTrue(ok, msg)

        content = bashrc_path.read_text(encoding='utf-8')
        self.assertNotIn(BLOCK_BEGIN, content)

if __name__ == '__main__':
    unittest.main()
