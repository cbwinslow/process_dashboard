"""
SNMP monitoring capabilities for Process Dashboard.
This version disables SNMP features if pysnmp is not available or import fails.

Provides SNMP-based system and process monitoring functionality.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SNMPError(Exception):
    pass
class SNMPConnectionError(SNMPError):
    pass
class SNMPAuthenticationError(SNMPError):
    pass

class SNMPMonitor:
    """Stub SNMP monitor: SNMP is disabled due to missing pysnmp high-level API."""
    OIDS = {
        'system': {
            'description': '1.3.6.1.2.1.1.1.0',
            'uptime': '1.3.6.1.2.1.1.3.0',
            'name': '1.3.6.1.2.1.1.5.0',
            'location': '1.3.6.1.2.1.1.6.0'
        },
    }
    def __init__(self, *args, **kwargs):
        logger.warning("SNMPMonitor is disabled: pysnmp high-level API not available.")
        self.enabled = False
    def get_system_metrics(self) -> Dict[str, Any]:
        logger.error("SNMP is not available on this system.")
        return {}

