import asyncio
from app.core.database import SessionLocal
from app.modules.auth.models import User
from sqlalchemy import select


async def grant_role():
    async with SessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == "gjimenezdeza@gmail.com")
        )
        user = result.scalar_one_or_none()
        if user:
            roles = list(user.roles) if user.roles else []
            if "VENDEDOR" not in roles:
                roles.append("VENDEDOR")
                user.roles = roles
                await db.commit()
                print("Role VENDEDOR added successfully!")
            else:
                print("User already has VENDEDOR role.")
        else:
            print("User not found.")


if __name__ == "__main__":
    asyncio.run(grant_role())
