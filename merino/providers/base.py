from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseProvider(ABC):
    """
    Abstract class for suggestion providers.
    """

    @abstractmethod
    async def query(self, query: str) -> List[Dict[str, Any]]:
        ...

    def enabled_by_default(self) -> bool:
        return False

    def hidden(self) -> bool:
        return False

    def availability(self) -> str:
        if self.hidden():
            return "hidden"
        elif self.enabled_by_default():
            return "enabled_by_default"
        else:
            return "disabled_by_default"


class DefaultProvider:
    """
    Default on provider.
    """

    def enabled_by_default(self) -> bool:
        return True
