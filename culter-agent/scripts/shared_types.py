"""Shared types stub — from eon-core (minimal fallback for standalone mode)."""

from enum import Enum


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"
    PARTIAL = "partial"


class ContradictionType(str, Enum):
    NONE = "none"
    DATA_CONFLICT = "data_conflict"
    METHOD_CONFLICT = "method_conflict"
    INTERPRETATION_CONFLICT = "interpretation_conflict"
