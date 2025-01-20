from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCollector(ABC):
    """Base class for content collectors."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the collector with configuration."""
        self.config = config
        
    @abstractmethod
    async def collect(self) -> List[Dict[str, Any]]:
        """Collect content from the source."""
        pass
    
    @abstractmethod
    async def filter_content(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter collected content based on relevance."""
        pass
    
    def validate_config(self) -> bool:
        """Validate the collector configuration."""
        return True 