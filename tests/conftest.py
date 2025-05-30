"""
Pytest configuration for Process Dashboard tests.
"""

import pytest
import pytest_asyncio

# Set default fixture scope for asyncio
pytest_plugins = ("pytest_asyncio",)

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

