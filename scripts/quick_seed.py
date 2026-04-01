import asyncio
from app.core.database import SessionLocal
from app.modules.auth.models import User, Role, UserRole
from app.modules.auth.security import get_password_hash
from app.modules.organizations.models import Company, CompanyUser
from sqlalchemy import select


async def quick_seed():
    print("🌱 Iniciando Quick Seed para Smoke Test...")
    async with SessionLocal() as db:
        # 1. Asegurar roles
        roles_to_create = ["ADMIN", "VENDEDOR", "CLIENTE"]
        for rname in roles_to_create:
            stmt = select(Role).where(Role.name == rname)
            res = await db.execute(stmt)
            if not res.scalar_one_or_none():
                role = Role(name=rname)
                db.add(role)
        await db.commit()

        # 2. Asegurar compañía
        stmt = select(Company).limit(1)
        res = await db.execute(stmt)
        company = res.scalar_one_or_none()
        if not company:
            company = Company(name="Yastubo Test Corp", short_code="YSTB")
            db.add(company)
            await db.flush()

        # 3. Asegurar usuario admin
        stmt = select(User).where(User.email == "admin@yastubo.com")
        res = await db.execute(stmt)
        admin = res.scalar_one_or_none()
        if not admin:
            admin = User(
                email="admin@yastubo.com",
                full_name="Administrator",
                hashed_password=get_password_hash("password123"),
                is_active=True,
            )
            db.add(admin)
            await db.flush()

            # Asignar rol
            role_res = await db.execute(select(Role).where(Role.name == "ADMIN"))
            admin_role = role_res.scalar_one()
            db.add(UserRole(user_id=admin.id, role_id=admin_role.id))

            # Asociar a compañía
            db.add(CompanyUser(user_id=admin.id, company_id=company.id))

        await db.commit()
        print(f"✅ Seed completado. Admin: {admin.email}, Compañía: {company.name}")


if __name__ == "__main__":
    asyncio.run(quick_seed())
