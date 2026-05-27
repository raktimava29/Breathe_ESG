import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any


def payload_hash(payload: dict) -> str:
    """Hash business payload; ignore row index / parser metadata for dedup."""
    business = {
        k: v for k, v in payload.items() if not str(k).startswith("_")
    }
    canonical = json.dumps(business, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


class BaseIngestionParser(ABC):
    """Parse upstream rows into dict payloads for RawRecord."""

    @abstractmethod
    def parse_rows(self, content: bytes | str, metadata: dict | None = None) -> list[dict[str, Any]]:
        pass
