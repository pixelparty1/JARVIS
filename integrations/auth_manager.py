"""
Authentication Manager - Secure Credential Management

Centralized handling of OAuth tokens and API keys.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import os


@dataclass
class Credentials:
    """Credential storage."""
    service_name: str
    credential_type: str  # "oauth", "api_key", "basic"
    data: Dict[str, Any]
    created_at: str = None
    expires_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def is_expired(self) -> bool:
        """Check if credentials are expired."""
        if self.expires_at:
            return datetime.fromisoformat(self.expires_at) < datetime.now()
        return False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class AuthManager:
    """
    Centralized authentication manager.
    
    Features:
    - Store credentials securely (in-memory, can extend to vault)
    - OAuth token refresh
    - Credential rotation
    - Multi-service support
    """
    
    def __init__(self, config_dir: str = "./jarvis_config"):
        """
        Initialize auth manager.
        
        Args:
            config_dir: Directory for storing credentials
        """
        self.config_dir = config_dir
        self.credentials: Dict[str, Credentials] = {}
        self.refresh_callbacks: Dict[str, callable] = {}
        
        os.makedirs(config_dir, exist_ok=True)
        self._load_credentials()
    
    def store_credentials(self, service_name: str,
                         credential_type: str,
                         data: Dict[str, Any],
                         expires_in_hours: Optional[int] = None) -> None:
        """
        Store credentials.
        
        Args:
            service_name: Service name (gmail, github, etc.)
            credential_type: oauth, api_key, basic
            data: Credential data
            expires_in_hours: Optional expiration time
        """
        expires_at = None
        if expires_in_hours:
            expires_at = (datetime.now() + timedelta(hours=expires_in_hours)).isoformat()
        
        cred = Credentials(
            service_name=service_name,
            credential_type=credential_type,
            data=data,
            expires_at=expires_at
        )
        
        self.credentials[service_name] = cred
        self._save_credentials()
        print(f"✅ Credentials stored for {service_name}")
    
    def get_credentials(self, service_name: str) -> Optional[Credentials]:
        """Get credentials for a service."""
        cred = self.credentials.get(service_name)
        
        if cred and cred.is_expired():
            print(f"⚠️  Credentials expired for {service_name}")
            return None
        
        return cred
    
    def refresh_token(self, service_name: str) -> bool:
        """
        Refresh OAuth token.
        
        Args:
            service_name: Service name
            
        Returns:
            Success status
        """
        cred = self.credentials.get(service_name)
        if not cred or cred.credential_type != "oauth":
            return False
        
        # Call refresh callback if registered
        if service_name in self.refresh_callbacks:
            callback = self.refresh_callbacks[service_name]
            new_data = callback(cred.data)
            cred.data = new_data
            self._save_credentials()
            return True
        
        return False
    
    def register_refresh_callback(self, service_name: str,
                                 callback: callable) -> None:
        """
        Register a token refresh callback.
        
        Args:
            service_name: Service name
            callback: Function that takes old data, returns new data
        """
        self.refresh_callbacks[service_name] = callback
    
    def has_credentials(self, service_name: str) -> bool:
        """Check if credentials exist."""
        cred = self.credentials.get(service_name)
        return cred is not None and not cred.is_expired()
    
    def remove_credentials(self, service_name: str) -> bool:
        """Remove credentials for a service."""
        if service_name in self.credentials:
            del self.credentials[service_name]
            self._save_credentials()
            return True
        return False
    
    def _save_credentials(self) -> None:
        """Save credentials to file."""
        cred_file = os.path.join(self.config_dir, "credentials.json")
        
        cred_data = {
            name: cred.to_dict()
            for name, cred in self.credentials.items()
        }
        
        try:
            with open(cred_file, 'w') as f:
                json.dump(cred_data, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save credentials: {e}")
    
    def _load_credentials(self) -> None:
        """Load credentials from file."""
        cred_file = os.path.join(self.config_dir, "credentials.json")
        
        if not os.path.exists(cred_file):
            return
        
        try:
            with open(cred_file, 'r') as f:
                cred_data = json.load(f)
            
            for service_name, data in cred_data.items():
                self.credentials[service_name] = Credentials(
                    service_name=data['service_name'],
                    credential_type=data['credential_type'],
                    data=data['data'],
                    created_at=data.get('created_at'),
                    expires_at=data.get('expires_at')
                )
        except Exception as e:
            print(f"⚠️  Failed to load credentials: {e}")
    
    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered services."""
        return {
            name: {
                'type': cred.credential_type,
                'created_at': cred.created_at,
                'expires_at': cred.expires_at,
                'expired': cred.is_expired()
            }
            for name, cred in self.credentials.items()
        }
    
    def rotate_credentials(self, service_name: str,
                          new_data: Dict[str, Any]) -> bool:
        """Rotate credentials for a service."""
        cred = self.credentials.get(service_name)
        if not cred:
            return False
        
        cred.data = new_data
        cred.created_at = datetime.now().isoformat()
        self._save_credentials()
        return True


# Mock OAuth helper for testing
class MockOAuthProvider:
    """
    Mock OAuth provider for testing.
    
    In production, use proper OAuth libraries like authlib.
    """
    
    @staticmethod
    def generate_token(service_name: str) -> Dict[str, str]:
        """Generate a mock token."""
        return {
            'access_token': f'mock_token_{service_name}_{datetime.now().timestamp()}',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
    
    @staticmethod
    def refresh_token(old_token: str) -> Dict[str, str]:
        """Refresh a mock token."""
        return MockOAuthProvider.generate_token('refreshed')
