"""
Unit tests for utils.helpers module.
"""
import platform
from src.utils.helpers import get_config_path, human_readable_bytes

def test_human_readable_bytes():
    assert human_readable_bytes(1023) == '1023.0B'
    assert human_readable_bytes(1024) == '1.0KB'
    assert human_readable_bytes(1048576) == '1.0MB'

def test_get_config_path_linux(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'Linux')
    path = get_config_path('test.yaml')
    assert '.config/process-dashboard/test.yaml' in str(path)

def test_get_config_path_mac(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'Darwin')
    path = get_config_path('test.yaml')
    assert 'Library/Application Support/process-dashboard/test.yaml' in str(path)

def test_get_config_path_windows(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'Windows')
    path = get_config_path('test.yaml')
    assert 'process-dashboard' in str(path)
