#!/usr/bin/env python3
"""
Test script for P03_Translator
Tests parsing of JavaScript, JSON, and requirements.txt installer files.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.P03_Translator import P03_Translator

def test_translator():
    """Basic unit test for P03_Translator functionality."""
    print("=== P03_Translator Unit Test ===\n")
    
    # Initialize translator
    translator = P03_Translator()
    print("✓ Translator initialized\n")
    
    # Test 1: Parse JavaScript file
    print("Test 1: JavaScript Parsing")
    print("-" * 40)
    
    # Create sample JS file
    js_content = """
    // Sample Pinokio installer script
    module.exports = {
        run: async () => {
            // Install dependencies
            await shell.run("pip install torch torchvision");
            
            // Download model
            await fs.download(
                "https://example.com/model.bin",
                "./models/model.bin",
                { checksum: "sha256:abc123" }
            );
            
            // Clone repository
            await git.clone("https://github.com/example/repo.git");
            
            // Get user input
            const name = await input("Enter your name", "Anonymous");
            
            // Write config
            await fs.write("config.txt", name);
        }
    }
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(js_content)
        js_file = f.name
    
    recipe = translator.parse_js(js_file)
    print(f"Parsed {len(recipe)} steps from JavaScript:")
    for i, step in enumerate(recipe, 1):
        print(f"  {i}. {step['step_type']}: {step['params']}")
    print("✓ Test 1 passed\n")
    
    # Test 2: Parse JSON file
    print("Test 2: JSON Parsing")
    print("-" * 40)
    
    json_data = {
        "run": [
            {
                "method": "shell.run",
                "params": {
                    "command": "npm install",
                    "args": []
                }
            },
            {
                "method": "fs.download",
                "params": {
                    "url": "https://example.com/data.zip",
                    "destination": "./data.zip"
                }
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_data, f)
        json_file = f.name
    
    recipe = translator.parse_json(json_file)
    print(f"Parsed {len(recipe)} steps from JSON:")
    for i, step in enumerate(recipe, 1):
        print(f"  {i}. {step['step_type']}: {step['params']}")
    print("✓ Test 2 passed\n")
    
    # Test 3: Parse requirements.txt
    print("Test 3: Requirements.txt Parsing")
    print("-" * 40)
    
    requirements_content = """
    # Core dependencies
    numpy>=1.20.0
    pandas==1.3.0
    scikit-learn
    
    # Deep learning
    torch>=1.9.0
    transformers
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(requirements_content)
        req_file = f.name
    
    recipe = translator.parse_requirements(req_file)
    print(f"Parsed {len(recipe)} steps from requirements.txt:")
    for i, step in enumerate(recipe, 1):
        command = step['params']['command']
        print(f"  {i}. {command}")
    print("✓ Test 3 passed\n")
    
    # Cleanup temp files
    Path(js_file).unlink()
    Path(json_file).unlink()
    Path(req_file).unlink()
    
    print("=== All tests passed! ===")

if __name__ == "__main__":
    test_translator()