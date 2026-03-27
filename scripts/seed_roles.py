import asyncio
from sqlalchemy import select
from app.core.database import SessionLocal
from app.modules.auth.models import Role, Permission

ROLES_PERMISSIONS = {
    "ADMIN": [
        "users:manage",
        "plans:write",
        "plans:read",
        "emission:write",
        "audit:read",
    ],
    "VENDEDOR": ["plans:read", "emission:write"],
    "CLIENTE": ["plans:read", "portal:read"],
}


async def seed():
    async with SessionLocal() as session:
        # Create permissions
        all_permissions = set()
        for perms in ROLES_PERMISSIONS.values():
            all_permissions.update(perms)

        permission_objs = {}
        for perm_name in all_permissions:
            result = await session.execute(
                select(Permission).where(Permission.name == perm_name)
            )
            perm = result.scalar_one_or_none()
            if not perm:
                perm = Permission(name=perm_name)
                session.add(perm)
                print(f"Created permission: {perm_name}")
            permission_objs[perm_name] = perm

        await session.flush()

        # Create roles
        for role_name, perms in ROLES_PERMISSIONS.items():
            result = await session.execute(select(Role).where(Role.name == role_name))
            role = result.scalar_one_or_none()
            if not role:
                role = Role(name=role_name)
                session.add(role)
                print(f"Created role: {role_name}")

            # Update permissions
            role.permissions = [permission_objs[p] for p in perms]

        await session.commit()
        print("Seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed())
