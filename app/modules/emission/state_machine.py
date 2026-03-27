from enum import Enum


class PolicyStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    ACTIVE = "ACTIVE"
    IN_ARREARS = "IN_ARREARS"  # en mora
    CANCELLED = "CANCELLED"
    CASE_REPORTED = "CASE_REPORTED"  # caso reportado
    CASE_IN_PROGRESS = "CASE_IN_PROGRESS"
    CASE_CLOSED = "CASE_CLOSED"


VALID_TRANSITIONS = {
    PolicyStatus.DRAFT: [PolicyStatus.PENDING_PAYMENT, PolicyStatus.CANCELLED],
    PolicyStatus.PENDING_PAYMENT: [
        PolicyStatus.ACTIVE,
        PolicyStatus.CANCELLED,
        PolicyStatus.IN_ARREARS,
    ],
    PolicyStatus.ACTIVE: [
        PolicyStatus.IN_ARREARS,
        PolicyStatus.CANCELLED,
        PolicyStatus.CASE_REPORTED,
    ],
    PolicyStatus.IN_ARREARS: [PolicyStatus.ACTIVE, PolicyStatus.CANCELLED],
    PolicyStatus.CASE_REPORTED: [PolicyStatus.CASE_IN_PROGRESS, PolicyStatus.CANCELLED],
    PolicyStatus.CASE_IN_PROGRESS: [PolicyStatus.CASE_CLOSED],
    PolicyStatus.CASE_CLOSED: [],
    PolicyStatus.CANCELLED: [],
}


def transition(current: PolicyStatus, target: PolicyStatus) -> PolicyStatus:
    if target not in VALID_TRANSITIONS.get(current, []):
        raise ValueError(f"Invalid transition: {current} → {target}")
    return target
