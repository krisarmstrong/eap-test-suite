import json
import os
import tempfile
import unittest
from radius_eap_tester.config import load_config, generate_config_template


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.temp_dir.name, "config.json")
        self.temp_config = os.path.join(self.temp_dir.name, "generated_config.json")
        generate_config_template(self.config_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_config(self):
        config = load_config(self.config_file)
        self.assertIn("server", config)
        self.assertIn("eap_methods", config)
        self.assertIn("ipaddress", config["server"])
        self.assertIn("tls", config["eap_methods"])

    def test_missing_config(self):
        with self.assertRaises(FileNotFoundError):
            load_config("nonexistent.json")

    def test_generate_config(self):
        generate_config_template(self.temp_config)
        self.assertTrue(os.path.exists(self.temp_config))
        with open(self.temp_config, "r") as f:
            config = json.load(f)
        self.assertIn("server", config)
        self.assertIn("eap_methods", config)
        os.unlink(self.temp_config)


if __name__ == "__main__":
    unittest.main()
