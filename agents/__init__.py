"""
Multi-Agent PRD Review System
Agents that collaborate to review and critique PRDs
"""

from .validator_agent import ValidatorAgent
from .skeptic_agent import SkepticAgent  # ← Uncommented!

__all__ = ['ValidatorAgent', 'SkepticAgent']  # ← Added back