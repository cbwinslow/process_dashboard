"""
SNMP monitoring capabilities for Process Dashboard.

Provides SNMP-based system and process monitoring functionality.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime
import socket
from pysnmp.hlapi import (
    SnmpEngine, CommunityData, UdpTransportTarget,
    ContextData, ObjectType, ObjectIdentity,
    getCmd, nextCmd
)

logger = logging.getLogger(__name__)

class SNMPError(Exception):
    """Base class for SNMP-related errors."""
    pass

class SNMPConnectionError(SNMPError):
    """Error connecting to SNMP agent."""
    pass

class SNMPAuthenticationError(SNMPError):
    """Error authenticating with SNMP agent."""
    pass

class SNMPMonitor:
    """SNMP monitoring for system and process metrics."""
    
    # Standard SNMP OIDs
    OIDS = {
        'system': {
            'description': '1.3.6.1.2.1.1.1.0',
            'uptime': '1.3.6.1.2.1.1.3.0',
            'name': '1.3.6.1.2.1.1.5.0',
            'location': '1.3.6.1.2.1.1.6.0'
        },
        'process': {
            'table': '1.3.6.1.2.1.25.4.2.1',
            'count': '1.3.6.1.2.1.25.1.6.0'
        },
        'resources': {
            'cpu_load': '1.3.6.1.2.1.25.3.3.1.2',
            'memory_total': '1.3.6.1.2.1.25.2.2.0',
            'memory_used': '1.3.6.1.2.1.25.2.3.1.6.1',
            'disk_storage': '1.3.6.1.2.1.25.2.3.1.5'
        }
    }

    def __init__(self, host: str = 'localhost', port: int = 161,
                 community: str = 'public', version: int = 2,
                 timeout: int = 5, retries: int = 3):
        """Initialize SNMP monitor.
        
        Args:
            host: Target host (default: localhost)
            port: SNMP port (default: 161)
            community: SNMP community string (default: public)
            version: SNMP version (1 or 2) (default: 2)
            timeout: Timeout in seconds (default: 5)
            retries: Number of retries (default: 3)
        """
        self.host = host
        self.port = port
        self.community = community
        self.version = version
        self.timeout = timeout
        self.retries = retries
        
        self.engine = SnmpEngine()
        self._verify_connection()

    def _verify_connection(self) -> None:
        """Verify SNMP connection.
        
        Raises:
            SNMPConnectionError: If connection fails
            SNMPAuthenticationError: If authentication fails
        """
        try:
            socket.gethostbyname(self.host)
            system_desc = self.get_system_info()
            if not system_desc:
                raise SNMPAuthenticationError("Failed to authenticate with SNMP agent")
        except socket.error as e:
            raise SNMPConnectionError(f"Failed to connect to {self.host}: {e}")

    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information.
        
        Returns:
            Dict containing system information.
        """
        info = {}
        for key, oid in self.OIDS['system'].items():
            value = self._get_snmp_value(oid)
            if value:
                info[key] = value
        return info

    def get_process_metrics(self) -> List[Dict[str, Any]]:
        """Get process-related metrics.
        
        Returns:
            List of dictionaries containing process metrics.
        """
        metrics = []
        process_table = self.OIDS['process']['table']
        
        for var_binds in self._walk_snmp(process_table):
            process = {}
            for var_bind in var_binds:
                oid = var_bind[0].prettyPrint()
                value = var_bind[1].prettyPrint()
                
                if '.1.' in oid:  # Process ID
                    process['pid'] = int(value)
                elif '.2.' in oid:  # Process name
                    process['name'] = value
                elif '.5.' in oid:  # Process status
                    process['status'] = value
                elif '.6.' in oid:  # CPU usage
                    process['cpu'] = int(value)
                elif '.7.' in oid:  # Memory usage
                    process['memory'] = int(value)
                    
            if process:
                metrics.append(process)
                
        return metrics

    def get_resource_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics.
        
        Returns:
            Dict containing resource metrics.
        """
        metrics = {}
        for key, oid in self.OIDS['resources'].items():
            value = self._get_snmp_value(oid)
            if value:
                metrics[key] = self._convert_value(key, value)
        return metrics

    def _get_snmp_value(self, oid: str) -> Optional[Any]:
        """Get single SNMP value.
        
        Args:
            oid: SNMP OID to query
            
        Returns:
            Query result or None if error occurs.
        """
        try:
            error_indication, error_status, error_index, var_binds = next(
                getCmd(self.engine,
                      CommunityData(self.community, mpModel=self.version),
                      UdpTransportTarget((self.host, self.port),
                                      timeout=self.timeout,
                                      retries=self.retries),
                      ContextData(),
                      ObjectType(ObjectIdentity(oid)))
            )
            
            if error_indication:
                logger.error(f"SNMP error: {error_indication}")
                return None
                
            if error_status:
                logger.error(f"SNMP error status: {error_status}")
                return None
                
            return var_binds[0][1].prettyPrint()
            
        except Exception as e:
            logger.error(f"Error in SNMP get: {e}")
            return None

    def _walk_snmp(self, oid: str) -> List[Tuple]:
        """Walk SNMP OID tree.
        
        Args:
            oid: Base OID to walk
            
        Returns:
            List of SNMP values.
        """
        try:
            walk_data = []
            for error_indication, error_status, error_index, var_binds in nextCmd(
                self.engine,
                CommunityData(self.community, mpModel=self.version),
                UdpTransportTarget((self.host, self.port),
                                timeout=self.timeout,
                                retries=self.retries),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False
            ):
                if error_indication:
                    logger.error(f"SNMP walk error: {error_indication}")
                    break
                elif error_status:
                    logger.error(f"SNMP walk error status: {error_status}")
                    break
                else:
                    walk_data.append(var_binds)
            return walk_data
            
        except Exception as e:
            logger.error(f"Error in SNMP walk: {e}")
            return []

    def _convert_value(self, key: str, value: str) -> Any:
        """Convert SNMP value to appropriate type.
        
        Args:
            key: Metric key
            value: Raw SNMP value
            
        Returns:
            Converted value.
        """
        try:
            if 'cpu' in key.lower():
                return float(value)
            elif 'memory' in key.lower() or 'disk' in key.lower():
                return int(value)
            return value
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting value {value}: {e}")
            return value

    def get_metrics_history(self, duration: int = 3600) -> Dict[str, List[Dict[str, Any]]]:
        """Get historical metrics for specified duration.
        
        Args:
            duration: Time period in seconds (default: 1 hour)
            
        Returns:
            Dict containing metric histories.
        """
        current_time = datetime.now()
        cutoff_time = current_time.timestamp() - duration
        
        metrics = {
            'system': self.get_system_info(),
            'processes': self.get_process_metrics(),
            'resources': self.get_resource_metrics()
        }
        
        metrics['timestamp'] = current_time.isoformat()
        return metrics

