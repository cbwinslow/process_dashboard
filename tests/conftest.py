"""
Test configuration for containerized testing.
"""

import os
import pytest
from typing import Generator
import docker

@pytest.fixture(scope="session")
def docker_client() -> Generator[docker.DockerClient, None, None]:
    """Create a Docker client for testing."""
    client = docker.from_env()
    yield client
    client.close()

@pytest.fixture(scope="session")
def container_environment(docker_client: docker.DockerClient) -> Generator[dict, None, None]:
    """Get environment variables from container."""
    container = docker_client.containers.get(os.getenv("HOSTNAME"))
    yield container.attrs["Config"]["Env"]

@pytest.fixture(scope="session")
def is_container() -> bool:
    """Check if tests are running in container."""
    return os.path.exists("/.dockerenv")

@pytest.fixture(scope="session")
def container_config_dir(is_container: bool) -> str:
    """Get configuration directory path."""
    if is_container:
        return "/home/dashboard/.config/process-dashboard"
    return os.path.expanduser("~/.config/process-dashboard")

@pytest.fixture(scope="session")
def container_log_dir(is_container: bool) -> str:
    """Get log directory path."""
    if is_container:
        return "/home/dashboard/.local/share/process-dashboard/logs"
    return os.path.expanduser("~/.local/share/process-dashboard/logs")

