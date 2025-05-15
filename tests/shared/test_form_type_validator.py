# tests/shared/test_form_type_validator.py

import unittest
from unittest.mock import patch, MagicMock, call
import sys, os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from utils.form_type_validator import FormTypeValidator
from config.config_loader import ConfigLoader

class TestFormTypeValidator(unittest.TestCase):
    
    def setUp(self):
        """Reset the form type validator state before each test"""
        FormTypeValidator._rules_loaded = False
        FormTypeValidator._known_form_types = set()
        FormTypeValidator._validation_map = {}
    
    @patch('utils.form_type_validator.ConfigLoader.load_form_type_rules')
    def test_load_form_type_rules(self, mock_load_rules):
        """Test loading form type rules from yaml file"""
        # Setup mock rules
        mock_rules = {
            "include_amendments": True,
            "form_type_rules": {
                "core": {
                    "registration": ["S-1", "S-3"],
                    "reporting": ["10-K", "10-Q", "8-K"],
                    "governance": {
                        "proxy": ["DEF 14A", "PRE 14A"]
                    }
                }
            }
        }
        mock_load_rules.return_value = mock_rules
        
        # Test loading rules
        FormTypeValidator._load_form_type_rules()
        
        # Check that known form types were loaded
        self.assertGreater(len(FormTypeValidator._known_form_types), 5)
        self.assertIn("10-K", FormTypeValidator._known_form_types)
        self.assertIn("DEF 14A", FormTypeValidator._known_form_types)
        
        # Check that validation map was created
        self.assertGreater(len(FormTypeValidator._validation_map), 5)
        self.assertIn("10-K", FormTypeValidator._validation_map)
        
        # Check if amendments are included
        self.assertIn("10-K/A", FormTypeValidator._known_form_types)
    
    def test_is_valid_form_type(self):
        """Test the is_valid_form_type method"""
        # Reset state
        FormTypeValidator._rules_loaded = False
        
        # Test various forms
        self.assertTrue(FormTypeValidator.is_valid_form_type("10-K"))
        self.assertTrue(FormTypeValidator.is_valid_form_type("10K"))
        self.assertTrue(FormTypeValidator.is_valid_form_type("8-K"))
        self.assertTrue(FormTypeValidator.is_valid_form_type("8K"))
        self.assertTrue(FormTypeValidator.is_valid_form_type("DEF 14A"))
        self.assertTrue(FormTypeValidator.is_valid_form_type("DEFA14A"))
        self.assertTrue(FormTypeValidator.is_valid_form_type("S-1/A"))
        
        # Test invalid forms
        self.assertFalse(FormTypeValidator.is_valid_form_type("XYZ"))
        self.assertFalse(FormTypeValidator.is_valid_form_type("ABC"))
    
    def test_validate_form_types(self):
        """Test form type validation with real function"""
        # Test known forms
        forms = ["10-K", "8-K", "10-Q"]
        result = FormTypeValidator.validate_form_types(forms)
        
        # Should preserve original forms
        self.assertEqual(result, forms)
        
        # Test unknown forms - this will actually log warnings but we don't capture them in this test
        forms = ["10-K", "XYZ", "ABC"]
        result = FormTypeValidator.validate_form_types(forms)
        
        # Should still preserve original forms even if unknown
        self.assertEqual(result, forms)
        
        # Test empty list
        result = FormTypeValidator.validate_form_types([])
        self.assertEqual(result, [])
    
    @patch('utils.form_type_validator.log_warn')
    def test_validate_warnings(self, mock_log_warn):
        """Test that warnings are logged for unknown forms"""
        # Reset state
        FormTypeValidator._rules_loaded = False
        FormTypeValidator._known_form_types = {"10-K", "8-K", "10-Q"}
        FormTypeValidator._validation_map = {"10-K": "10-K", "8-K": "8-K", "10-Q": "10-Q"}
        
        # Test unknown forms
        forms = ["10-K", "XYZ", "ABC"]
        result = FormTypeValidator.validate_form_types(forms)
        
        # Should log two warnings
        self.assertEqual(mock_log_warn.call_count, 2)
    
    @patch('config.config_loader.ConfigLoader.get_default_include_forms')
    def test_get_validated_form_types(self, mock_get_defaults):
        """Test the get_validated_form_types method"""
        # Setup mock
        mock_get_defaults.return_value = ["10-K", "8-K", "10-Q"]
        
        # Test with None (should use defaults)
        self.assertEqual(FormTypeValidator.get_validated_form_types(None), ["10-K", "8-K", "10-Q"])
        mock_get_defaults.assert_called_once()
        
        # Test with valid forms - should preserve original forms
        mock_get_defaults.reset_mock()
        forms = ["10K", "8K"]
        result = FormTypeValidator.get_validated_form_types(forms)
        self.assertEqual(result, forms)  # Original forms preserved
        mock_get_defaults.assert_not_called()
    
    def test_original_code_preservation(self):
        """Test that original form codes are preserved"""
        # Test various forms
        test_forms = [
            "10-K", "10K", "8-K", "8K", 
            "DEFA14A", "DEF 14A", 
            "S-1/A", "s-1/a"  # Case should be preserved
        ]
        
        result = FormTypeValidator.get_validated_form_types(test_forms)
        
        # Result should be identical to input - preserving case and format
        self.assertEqual(result, test_forms)


if __name__ == '__main__':
    unittest.main()