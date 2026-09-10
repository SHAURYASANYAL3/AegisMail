from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ThreatIntelProvider(ABC):
    """
    Abstract interface for all Threat Intelligence providers.
    Every provider must return standardized normalized enrichment data.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def lookup_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def lookup_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def lookup_hash(self, sha256: str) -> Optional[Dict[str, Any]]:
        pass
