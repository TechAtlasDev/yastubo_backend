import pytest
from app.modules.emission.state_machine import PolicyStatus, transition


def test_valid_transition_draft_to_pending_payment():
    assert (
        transition(PolicyStatus.DRAFT, PolicyStatus.PENDING_PAYMENT)
        == PolicyStatus.PENDING_PAYMENT
    )


def test_valid_transition_pending_payment_to_active():
    assert (
        transition(PolicyStatus.PENDING_PAYMENT, PolicyStatus.ACTIVE)
        == PolicyStatus.ACTIVE
    )


def test_invalid_transition_active_to_draft_raises_error():
    with pytest.raises(ValueError, match="Invalid transition"):
        transition(PolicyStatus.ACTIVE, PolicyStatus.DRAFT)


def test_invalid_transition_cancelled_to_active_raises_error():
    with pytest.raises(ValueError, match="Invalid transition"):
        transition(PolicyStatus.CANCELLED, PolicyStatus.ACTIVE)


def test_terminal_state_case_closed_raises_error():
    with pytest.raises(ValueError, match="Invalid transition"):
        transition(PolicyStatus.CASE_CLOSED, PolicyStatus.CANCELLED)
