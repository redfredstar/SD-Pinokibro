"""
P03-Test_Translator.py - Test Suite for P03_Translator

This test suite validates the functionality of the P03_Translator module,
ensuring it correctly parses various installer formats (.json, .js, .txt)
into standardized recipe steps while preserving execution order.

Author: Pinokiobro Architect
Phase: P03 - The Universal Translator
"""

import unittest
import tempfile
import os
import json
import sys
from unittest.mock import patch

# Add the App directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from App.Utils.P03_Translator import P03_Translator, RecipeStep


class TestP03Translator(unittest.TestCase):
    """Test cases for the P03_Translator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.translator = P03_Translator()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_initialization(self):
        """Test that Translator initializes with correct regex patterns."""
        self.assertIsInstance(self.translator.js_patterns, dict)
        self.assertIn('shell.run', self.translator.js_patterns)
        self.assertIn('fs.download', self.translator.js_patterns)
        self.assertIn('git.clone', self.translator.js_patterns)
        
    def test_parse_json_list_of_commands(self):
        """Test parsing a JSON file with a list of shell commands."""
        # Create a test JSON file
        json_content = [
            "echo 'Hello World'",
            "pip install numpy",
            {"type": "shell", "command": "python setup.py install"}
        ]
        json_file = os.path.join(self.temp_dir, "install.json")
        with open(json_file, 'w') as f:
            json.dump(json_content, f)
            
        # Parse the file
        recipe = self.translator.parse_json(json_file)
        
        # Verify the recipe
        self.assertEqual(len(recipe), 3)
        self.assertEqual(recipe[0].step_type, 'shell')
        self.assertEqual(recipe[0].params['command'], "echo 'Hello World'")
        self.assertEqual(recipe[1].step_type, 'shell')
        self.assertEqual(recipe[1].params['command'], "pip install numpy")
        self.assertEqual(recipe[2].step_type, 'shell')
        self.assertEqual(recipe[2].params['command'], "python setup.py install")
        
    def test_parse_json_single_command(self):
        """Test parsing a JSON file with a single command object."""
        # Create a test JSON file
        json_content = {
            "type": "download",
            "url": "https://example.com/file.zip",
            "dest": "/tmp/file.zip"
        }
        json_file = os.path.join(self.temp_dir, "install.json")
        with open(json_file, 'w') as f:
            json.dump(json_content, f)
            
        # Parse the file
        recipe = self.translator.parse_json(json_file)
        
        # Verify the recipe
        self.assertEqual(len(recipe), 1)
        self.assertEqual(recipe[0].step_type, 'download')
        self.assertEqual(recipe[0].params['url'], "https://example.com/file.zip")
        self.assertEqual(recipe[0].params['dest'], "/tmp/file.zip")
        
    def test_parse_js_shell_commands(self):
        """Test parsing a JS file with shell.run commands."""
        # Create a test JS file
        js_content = """
        // Installation script
        shell.run("echo 'Starting installation'");
        shell.run("pip install requests");
        shell.run("python -m pip install --upgrade pip");
        """
        js_file = os.path.join(self.temp_dir, "install.js")
        with open(js_file, 'w') as f:
            f.write(js_content)
            
        # Parse the file
        recipe = self.translator.parse_js(js_file)
        
        # Verify the recipe
        self.assertEqual(len(recipe), 3)
        self.assertEqual(recipe[0].step_type, 'shell')
        self.assertEqual(recipe[0].params['command'], "echo 'Starting installation'")
        self.assertEqual(recipe[1].step_type, 'shell')
        self.assertEqual(recipe[1].params['command'], "pip install requests")
        self.assertEqual(recipe[2].step_type, 'shell')
        self.assertEqual(recipe[2].params['command'], "python -m pip install --upgrade pip")
        
    def test_parse_js_mixed_commands(self):
        """Test parsing a JS file with mixed command types."""
        # Create a test JS file
        js_content = """
        // Mixed installation script
        shell.run("mkdir -p /tmp/app");
        fs.download("https://example.com/app.zip", "/tmp/app.zip");
        git.clone("https://github.com/user/repo.git", "/tmp/repo");
        pip.install("numpy");
        """
        js_file = os.path.join(self.temp_dir, "install.js")
        with open(js_file, 'w') as f:
            f.write(js_content)
            
        # Parse the file
        recipe = self.translator.parse_js(js_file)
        
        # Verify the recipe
        self.assertEqual(len(recipe), 4)
        self.assertEqual(recipe[0].step_type, 'shell')
        self.assertEqual(recipe[1].step_type, 'download')
        self.assertEqual(recipe[2].step_type, 'git_clone')
        self.assertEqual(recipe[3].step_type, 'pip_install')
        
    def test_parse_requirements_txt(self):
        """Test parsing a requirements.txt file."""
        # Create a test requirements.txt file
        req_content = """
        # This is a comment
        numpy>=1.19.0
        pandas
        matplotlib>=3.3.0
        # Another comment
        scikit-learn
        """
        req_file = os.path.join(self.temp_dir, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write(req_content)
            
        # Parse the file
        recipe = self.translator.parse_requirements_txt(req_file)
        
        # Verify the recipe
        self.assertEqual(len(recipe), 4)
        self.assertEqual(recipe[0].step_type, 'pip_install')
        self.assertEqual(recipe[0].params['package'], "numpy>=1.19.0")
        self.assertEqual(recipe[1].params['package'], "pandas")
        self.assertEqual(recipe[2].params['package'], "matplotlib>=3.3.0")
        self.assertEqual(recipe[3].params['package'], "scikit-learn")
        
    def test_parse_file_by_extension(self):
        """Test that parse_file correctly routes to the right parser based on extension."""
        # Test JSON file
        json_content = ["echo 'test'"]
        json_file = os.path.join(self.temp_dir, "install.json")
        with open(json_file, 'w') as f:
            json.dump(json_content, f)
        recipe = self.translator.parse_file(json_file)
        self.assertEqual(len(recipe), 1)
        self.assertEqual(recipe[0].step_type, 'shell')
        
        # Test JS file
        js_content = 'shell.run("echo test");'
        js_file = os.path.join(self.temp_dir, "install.js")
        with open(js_file, 'w') as f:
            f.write(js_content)
        recipe = self.translator.parse_file(js_file)
        self.assertEqual(len(recipe), 1)
        self.assertEqual(recipe[0].step_type, 'shell')
        
        # Test requirements.txt file
        req_content = "numpy"
        req_file = os.path.join(self.temp_dir, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write(req_content)
        recipe = self.translator.parse_file(req_file)
        self.assertEqual(len(recipe), 1)
        self.assertEqual(recipe[0].step_type, 'pip_install')
        
    def test_parse_nonexistent_file(self):
        """Test parsing a non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.translator.parse_file("/nonexistent/file.json")
            
    def test_parse_unsupported_file_format(self):
        """Test parsing an unsupported file format raises ValueError."""
        # Create a test file with unsupported extension
        unsupported_file = os.path.join(self.temp_dir, "install.xml")
        with open(unsupported_file, 'w') as f:
            f.write("<test></test>")
            
        with self.assertRaises(ValueError):
            self.translator.parse_file(unsupported_file)
            
    def test_validate_recipe_valid(self):
        """Test validating a valid recipe returns True."""
        recipe = [
            RecipeStep(step_type='shell', params={'command': 'echo test'}),
            RecipeStep(step_type='download', params={'url': 'https://example.com/file.zip'}),
            RecipeStep(step_type='pip_install', params={'package': 'numpy'})
        ]
        self.assertTrue(self.translator.validate_recipe(recipe))
        
    def test_validate_recipe_invalid(self):
        """Test validating an invalid recipe returns False."""
        # Missing required parameter
        recipe = [
            RecipeStep(step_type='shell', params={}),  # Missing 'command'
            RecipeStep(step_type='download', params={'url': 'https://example.com/file.zip'})
        ]
        self.assertFalse(self.translator.validate_recipe(recipe))
        
    def test_validate_empty_recipe(self):
        """Test validating an empty recipe returns False."""
        recipe = []
        self.assertFalse(self.translator.validate_recipe(recipe))
        
    def test_js_command_order_preservation(self):
        """Test that JS commands are parsed in the correct order."""
        js_content = """
        // Commands in specific order
        shell.run("first command");
        shell.run("second command");
        shell.run("third command");
        """
        js_file = os.path.join(self.temp_dir, "install.js")
        with open(js_file, 'w') as f:
            f.write(js_content)
            
        recipe = self.translator.parse_js(js_file)
        
        # Verify order is preserved
        self.assertEqual(recipe[0].params['command'], "first command")
        self.assertEqual(recipe[1].params['command'], "second command")
        self.assertEqual(recipe[2].params['command'], "third command")
        
    def test_js_optional_parameters(self):
        """Test that JS optional parameters are correctly parsed."""
        js_content = """
        fs.download("https://example.com/file.zip", "/tmp/destination");
        git.clone("https://github.com/user/repo.git");
        """
        js_file = os.path.join(self.temp_dir, "install.js")
        with open(js_file, 'w') as f:
            f.write(js_content)
            
        recipe = self.translator.parse_js(js_file)
        
        # Verify optional parameters
        self.assertEqual(recipe[0].step_type, 'download')
        self.assertEqual(recipe[0].params['url'], "https://example.com/file.zip")
        self.assertEqual(recipe[0].params['dest'], "/tmp/destination")
        
        self.assertEqual(recipe[1].step_type, 'git_clone')
        self.assertEqual(recipe[1].params['repo'], "https://github.com/user/repo.git")
        self.assertNotIn('dest', recipe[1].params)  # Optional parameter not provided


class TestRecipeStep(unittest.TestCase):
    """Test cases for the RecipeStep dataclass."""
    
    def test_recipe_step_creation(self):
        """Test creating a RecipeStep object."""
        step = RecipeStep(
            step_type='shell',
            params={'command': 'echo test'},
            metadata={'line_number': 1}
        )
        
        self.assertEqual(step.step_type, 'shell')
        self.assertEqual(step.params['command'], 'echo test')
        self.assertEqual(step.metadata['line_number'], 1)
        
    def test_recipe_step_default_metadata(self):
        """Test that metadata is initialized if not provided."""
        step = RecipeStep(
            step_type='shell',
            params={'command': 'echo test'}
        )
        
        self.assertEqual(step.metadata, {})


if __name__ == '__main__':
    # Configure logging to see debug output
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Run the tests
    unittest.main(verbosity=2)