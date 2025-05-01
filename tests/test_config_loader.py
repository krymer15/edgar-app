import sys
from utils.get_project_root import get_project_root
sys.path.append(get_project_root())

import unittest
from utils.config_loader import ConfigLoader

class TestConfigLoader(unittest.TestCase):
    def test_database_url_present(self):
        config = ConfigLoader.load_config()
        db_url = config.get("database", {}).get("url")
        self.assertIsNotNone(db_url, "DATABASE_URL not found in config")
        self.assertIn("postgresql://", db_url)

if __name__ == "__main__":
    unittest.main()
