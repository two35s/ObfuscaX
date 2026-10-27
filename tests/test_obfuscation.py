import base64
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dynamic_obfuscation import dynamic_obfuscate
from obfuscator import pick_obf
from static_obfuscation import static_obfuscate


class ObfuscationTests(unittest.TestCase):
    def test_static_wrapper_decodes_as_utf16le(self):
        script = "Write-Host 'hello'"
        out = static_obfuscate(script.encode()).decode()
        encoded = out.strip().splitlines()[-1].split()[-1]
        self.assertEqual(base64.b64decode(encoded).decode("utf-16-le"), script)

    def test_dynamic_roundtrip(self):
        script = "Write-Host 'hello'"
        out = dynamic_obfuscate(script.encode(), xor_key=77).decode()
        encoded = out.split('$encoded = "')[1].split('"')[0]
        data = base64.b64decode(encoded)
        self.assertEqual(bytes(b ^ 77 for b in data), script.encode())

    def test_config_uses_jobs_schema(self):
        data = json.loads((ROOT / "config.json").read_text())
        self.assertIsInstance(data["jobs"], list)

    def test_exe_rejects_obfuscation(self):
        with self.assertRaises(ValueError):
            pick_obf("exe", "static")
        self.assertEqual(pick_obf("exe", None), "none")
        self.assertEqual(pick_obf("ps1", None), "static")


if __name__ == "__main__":
    unittest.main()
