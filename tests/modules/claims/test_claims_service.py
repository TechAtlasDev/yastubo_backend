import pytest
import uuid
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.claims import service, schemas
from app.modules.claims.state_machine import ClaimStatus


@pytest.mark.asyncio
async def test_create_claim_service(
    db_session: AsyncSession, admin_user, issued_policy
):
    # Setup
    policy_id = uuid.UUID(issued_policy["id"])
    beneficiary_id = uuid.UUID(issued_policy["beneficiaries"][0]["id"])

    claim_in = schemas.ClaimCreate(
        policy_id=policy_id, beneficiary_id=beneficiary_id, description="Test claim"
    )

    # Execute
    with patch(
        "app.modules.claims.service.redis_client.publish", new_callable=AsyncMock
    ) as mock_publish:
        claim = await service.create_claim(
            db=db_session, claim_in=claim_in, user_id=admin_user.id
        )

        # Verify
        assert claim.policy_id == policy_id
        assert claim.beneficiary_id == beneficiary_id
        assert claim.status == ClaimStatus.REPORTED
        mock_publish.assert_called_once()


@pytest.mark.asyncio
async def test_update_claim_status_service(
    db_session: AsyncSession, admin_user, issued_policy
):
    # Setup
    policy_id = uuid.UUID(issued_policy["id"])
    beneficiary_id = uuid.UUID(issued_policy["beneficiaries"][0]["id"])

    claim_in = schemas.ClaimCreate(
        policy_id=policy_id, beneficiary_id=beneficiary_id, description="Test claim"
    )

    with patch(
        "app.modules.claims.service.redis_client.publish", new_callable=AsyncMock
    ):
        claim = await service.create_claim(
            db=db_session, claim_in=claim_in, user_id=admin_user.id
        )

    # Transition REPORTED -> IN_REVIEW
    status_update = schemas.ClaimUpdateStatus(status=ClaimStatus.IN_REVIEW)
    updated_claim = await service.update_claim_status(
        db=db_session,
        claim_id=claim.id,
        status_update=status_update,
        user_id=admin_user.id,
    )
    assert updated_claim.status == ClaimStatus.IN_REVIEW

    # Transition IN_REVIEW -> APPROVED (this should enqueue a job)
    status_update = schemas.ClaimUpdateStatus(status=ClaimStatus.APPROVED)
    with patch("arq.create_pool", new_callable=AsyncMock) as mock_create_pool:
        mock_arq = AsyncMock()
        mock_create_pool.return_value = mock_arq

        final_claim = await service.update_claim_status(
            db=db_session,
            claim_id=claim.id,
            status_update=status_update,
            user_id=admin_user.id,
        )

        assert final_claim.status == ClaimStatus.APPROVED
        assert final_claim.resolved_at is not None
        mock_create_pool.assert_called_once()
        mock_arq.enqueue_job.assert_called_once_with(
            "process_approved_claim",
            str(final_claim.id),
            str(final_claim.beneficiary_id),
        )


@pytest.mark.asyncio
async def test_add_claim_expense_service(
    db_session: AsyncSession, admin_user, issued_policy
):
    # Setup
    policy_id = uuid.UUID(issued_policy["id"])
    beneficiary_id = uuid.UUID(issued_policy["beneficiaries"][0]["id"])

    claim_in = schemas.ClaimCreate(
        policy_id=policy_id, beneficiary_id=beneficiary_id, description="Test claim"
    )

    with patch(
        "app.modules.claims.service.redis_client.publish", new_callable=AsyncMock
    ):
        claim = await service.create_claim(
            db=db_session, claim_in=claim_in, user_id=admin_user.id
        )

    expense_in = schemas.ClaimExpenseCreate(
        amount=150.0, currency="USD", expense_type="FUNERAL"
    )

    # Execute
    expense = await service.add_claim_expense(
        db=db_session, claim_id=claim.id, expense_in=expense_in, user_id=admin_user.id
    )

    # Verify
    assert expense.amount == 150.0
    assert expense.expense_type == "FUNERAL"
    assert expense.claim_id == claim.id
