"""
Unit tests for config.settings (DashboardConfig).
"""
import pytest
from src.config.settings import DashboardConfig, save_config, load_config, create_default_config

def test_load_and_save(tmp_path, monkeypatch):
    config = create_default_config()
    config_path = tmp_path / 'test_config.yaml'
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path))
    save_config(config)
    loaded = load_config()
    assert loaded is not None
    assert loaded.theme.background_color == config.theme.background_color

def test_set_and_get():
    config = create_default_config()
    config.theme.background_color = '#00FF00'
    assert config.theme.background_color == '#00FF00'
