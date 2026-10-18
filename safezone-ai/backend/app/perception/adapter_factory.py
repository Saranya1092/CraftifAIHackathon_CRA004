"""Factory that returns the correct perception adapter based on configuration."""
from __future__ import annotations

import logging

from app.perception.base_adapter import BaseAdapter

logger = logging.getLogger(__name__)


def get_adapter(adapter_type: str) -> BaseAdapter:
    """
    Return a perception adapter instance.

    adapter_type values:
      "simulated"  – deterministic fake events (testing / UI dev)
      "pipegen"    – reads JSON output from a running PipeGen/DeepStream pipeline
      "deepstream" – alias for pipegen (same output format)
    """
    t = adapter_type.lower()
    if t == "simulated":
        from app.perception.simulated_adapter import SimulatedAdapter
        logger.warning(
            "Using SIMULATED perception adapter. "
            "Results are NOT real AI inference."
        )
        return SimulatedAdapter()
    elif t in ("pipegen", "deepstream"):
        from app.perception.pipegen_adapter import PipeGenAdapter
        logger.info("Using PipeGen/DeepStream perception adapter.")
        return PipeGenAdapter()
    else:
        raise ValueError(f"Unknown perception adapter: {adapter_type!r}")
