import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_manager import ConfigManager

def test_config_manager_key_save_load():
    """Test 2.1: Save and load API key with encryption"""
    test_config_path = Path("test_config.enc")
    if test_config_path.exists():
        os.remove(test_config_path)
    
    # Initialize with custom path for testing
    mgr = ConfigManager(config_path=test_config_path)
    
    test_key = "AIzaSy_test_gemini_key_123"
    
    # 1. Set key
    mgr.set_api_key(test_key)
    
    # 2. Check if file exists
    assert test_config_path.exists()
    
    # 3. Load key back
    loaded_key = mgr.get_api_key()
    assert loaded_key == test_key
    
    # 4. Content should be encrypted (not raw text)
    with open(test_config_path, "rb") as f:
        raw_data = f.read()
        assert test_key.encode() not in raw_data
        
    # Cleanup
    os.remove(test_config_path)

def test_config_init_no_file():
    """Test if manager handles missing file correctly"""
    test_config_path = Path("missing_config.enc")
    mgr = ConfigManager(config_path=test_config_path)
    assert mgr.get_api_key() is None
    assert mgr.has_api_key() is False
