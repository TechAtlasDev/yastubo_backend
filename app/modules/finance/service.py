import uuid
from decimal import Decimal
from typing import List, Optional, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.finance.models import CompanyCommissionUser, BusinessUnitCommissionUser


class CommissionService:
    @staticmethod
    async def calculate_dispersion(
        db: AsyncSession,
        amount: float,
        company_id: uuid.UUID,
        business_unit_id: Optional[uuid.UUID] = None,
    ) -> List[Dict]:
        """
        Calculates how a payment amount should be dispersed among actors.
        Actors can be defined at Company level and Business Unit level.
        Percentages are absolute (0-100% of the total amount).

        Throws ValueError if total percentage exceeds 100%.
        """
        amount_dec = Decimal(str(amount))
        splits = []
        total_percentage = Decimal("0.0")

        # 1. Fetch Company Level Commissions
        res_company = await db.execute(
            select(CompanyCommissionUser).where(
                CompanyCommissionUser.company_id == company_id
            )
        )
        company_commissions = res_company.scalars().all()

        for cc in company_commissions:
            percentage = Decimal(str(cc.commission_percentage))
            total_percentage += percentage
            splits.append(
                {
                    "user_id": cc.user_id,
                    "percentage": float(percentage),
                    "amount": float(
                        (amount_dec * percentage / Decimal("100.0")).quantize(
                            Decimal("0.01")
                        )
                    ),
                    "level": "COMPANY",
                }
            )

        # 2. Fetch Business Unit Level Commissions
        if business_unit_id:
            res_bu = await db.execute(
                select(BusinessUnitCommissionUser).where(
                    BusinessUnitCommissionUser.business_unit_id == business_unit_id
                )
            )
            bu_commissions = res_bu.scalars().all()

            for buc in bu_commissions:
                percentage = Decimal(str(buc.commission_percentage))
                total_percentage += percentage
                splits.append(
                    {
                        "user_id": buc.user_id,
                        "percentage": float(percentage),
                        "amount": float(
                            (amount_dec * percentage / Decimal("100.0")).quantize(
                                Decimal("0.01")
                            )
                        ),
                        "level": "BUSINESS_UNIT",
                    }
                )

        if total_percentage > Decimal("100.0"):
            raise ValueError(
                f"Total commission percentage ({total_percentage}%) exceeds 100%"
            )

        return splits
