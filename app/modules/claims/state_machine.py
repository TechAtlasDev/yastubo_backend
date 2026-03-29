from enum import Enum


class ClaimStatus(str, Enum):
    REPORTED = "REPORTED"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PAID = "PAID"


class InvalidTransitionError(Exception):
    pass


def can_transition(current_status: str, next_status: str) -> bool:
    """Valida si una transición de estado de siniestro es permitida."""
    valid_transitions = {
        ClaimStatus.REPORTED: [ClaimStatus.IN_REVIEW, ClaimStatus.REJECTED],
        ClaimStatus.IN_REVIEW: [ClaimStatus.APPROVED, ClaimStatus.REJECTED],
        ClaimStatus.APPROVED: [ClaimStatus.PAID],
        ClaimStatus.REJECTED: [],
        ClaimStatus.PAID: [],
    }

    if current_status not in valid_transitions:
        return False

    return next_status in valid_transitions[current_status]
