"""
Tests for the DashboardConfig class.
"""

import os
import json
import tempfile
from pathlib import Path
import pytest
from config.settings import DashboardConfig, load_or_create_config

@pytest.fixture
def temp_config_file():
    """Create a temporary config file."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        yield Path(f.name)
    os.unlink(f.name)

@pytest.fixture
def config(temp_config_file):
    """Create a DashboardConfig instance with temporary file."""
    return DashboardConfig(temp_config_file)

def test_default_config():
    """Test default configuration values."""
    config = DashboardConfig()
    
    assert config.matrix_theme is True
    assert config.theme == "dark"
    assert config.css_path is None
    assert config.update_interval == 2
    assert config.history_length == 60
    assert config.show_system is True
    assert config.show_children is True
    assert config.confirm_actions is True
    assert config.allow_kill is True
    assert config.allow_priority is True

def test_save_and_load(config, temp_config_file):
    """Test saving and loading configuration."""
    # Modify some settings
    config.matrix_theme = False
    config.theme = "light"
    config.update_interval = 5
    
    # Save configuration
    config.save()
    
    # Load in new instance
    new_config = DashboardConfig(temp_config_file)
    
    # Verify settings were preserved
    assert new_config.matrix_theme is False
    assert new_config.theme == "light"
    assert new_config.update_interval == 5

def test_load_invalid_file(temp_config_file):
    """Test loading invalid configuration file."""
    # Write invalid JSON
    with open(temp_config_file, 'w') as f:
        f.write("invalid json")
    
    # Should use defaults when file is invalid
    config = DashboardConfig(temp_config_file)
    assert config.matrix_theme is True
    assert config.theme == "dark"

def test_get_set_config_values(config):
    """Test getting and setting configuration values."""
    # Test setting values
    config.set("theme", "light")
    config.set("custom_colors.background", "#ffffff")
    
    # Test getting values
    assert config.get("theme") == "light"
    assert config.get("custom_colors.background") == "#ffffff"
    
    # Test getting non-existent value
    assert config.get("nonexistent", "default") == "default"

def test_reset_config(config):
    """Test resetting configuration to defaults."""
    # Modify settings
    config.matrix_theme = False
    config.theme = "light"
    config.update_interval = 5
    
    # Reset configuration
    config.reset()
    
    # Verify defaults were restored
    assert config.matrix_theme is True
    assert config.theme == "dark"
    assert config.update_interval == 2

def test_nested_config_values(config):
    """Test handling of nested configuration values."""
    # Set nested values
    config.set("custom_colors.background", "#000000")
    config.set("custom_colors.foreground", "#00ff00")
    
    # Save and reload
    config.save()
    new_config = DashboardConfig(config.config_path)
    
    # Verify nested values were preserved
    assert new_config.get("custom_colors.background") == "#000000"
    assert new_config.get("custom_colors.foreground") == "#00ff00"

def test_load_or_create_config():
    """Test load_or_create_config utility function."""
    # Test with non-existent file
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.json"
        config = load_or_create_config(config_path)
        
        # Should create new config with defaults
        assert isinstance(config, DashboardConfig)
        assert config.matrix_theme is True
        assert config.theme == "dark"
        
        # File should be created
        assert config_path.exists()

def test_config_property_access(config):
    """Test property accessor methods."""
    # Test property setters
    config.matrix_theme = False
    config.theme = "light"
    config.update_interval = 5
    config.history_length = 120
    config.show_system = False
    config.show_children = False
    config.confirm_actions = False
    config.allow_kill = False
    config.allow_priority = False
    
    # Test property getters
    assert config.matrix_theme is False
    assert config.theme == "light"
    assert config.update_interval == 5
    assert config.history_length == 120
    assert config.show_system is False
    assert config.show_children is False
    assert config.confirm_actions is False
    assert config.allow_kill is False
    assert config.allow_priority is False

def test_config_validation(config):
    """Test configuration value validation."""
    # Test invalid update interval
    with pytest.raises(ValueError):
        config.update_interval = -1
    
    # Test invalid history length
    with pytest.raises(ValueError):
        config.history_length = 0
    
    # Test invalid theme
    with pytest.raises(ValueError):
        config.theme = "invalid"
