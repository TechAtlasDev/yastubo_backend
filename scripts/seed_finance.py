import asyncio
from sqlalchemy import select
from app.core.database import SessionLocal
from app.modules.finance.models import Currency, UnitOfMeasure
# Import other models to resolve relationships


async def seed_finance():
    async with SessionLocal() as db:
        # Currencies
        currencies = [
            {"code": "USD", "name": "United States Dollar", "symbol": "$"},
            {"code": "COP", "name": "Peso Colombiano", "symbol": "$"},
            {"code": "EUR", "name": "Euro", "symbol": "€"},
            {"code": "MXN", "name": "Peso Mexicano", "symbol": "$"},
        ]

        for cur_data in currencies:
            res = await db.execute(
                select(Currency).where(Currency.code == cur_data["code"])
            )
            if not res.scalar_one_or_none():
                db.add(Currency(**cur_data))
                print(f"Added Currency: {cur_data['code']}")

        # Units of Measure
        units = [
            {
                "id": 1,
                "name": {"en": "Sessions", "es": "Sesiones"},
                "measure_type": "integer",
            },
            {"id": 2, "name": {"en": "USD", "es": "USD"}, "measure_type": "decimal"},
            {
                "id": 3,
                "name": {"en": "No limits", "es": "Sin límite"},
                "measure_type": "none",
            },
            {
                "id": 4,
                "name": {"en": "Free text", "es": "Texto libre"},
                "measure_type": "text",
            },
            {"id": 5, "name": {"en": "Days", "es": "Días"}, "measure_type": "integer"},
            {
                "id": 6,
                "name": {"en": "Included", "es": "Incluido"},
                "measure_type": "none",
            },
            {
                "id": 7,
                "name": {"en": "Hours", "es": "Horas"},
                "measure_type": "integer",
            },
        ]

        for u_data in units:
            res = await db.execute(
                select(UnitOfMeasure).where(UnitOfMeasure.id == u_data["id"])
            )
            if not res.scalar_one_or_none():
                db.add(UnitOfMeasure(**u_data))
                print(f"Added Unit: {u_data['name']['es']}")

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed_finance())
