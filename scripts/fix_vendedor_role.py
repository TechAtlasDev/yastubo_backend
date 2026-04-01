import asyncio
from app.core.database import SessionLocal
from app.modules.auth.models import User, Role, UserRole
from sqlalchemy import select, insert


async def grant_role():
    async with SessionLocal() as db:
        # Buscar el usuario
        user_result = await db.execute(
            select(User).where(User.email == "gjimenezdeza@gmail.com")
        )
        user = user_result.scalar_one_or_none()

        # Buscar el rol
        role_result = await db.execute(select(Role).where(Role.name == "VENDEDOR"))
        role = role_result.scalar_one_or_none()

        if not user or not role:
            print(
                f"Error: Usuario ({'Encontrado' if user else 'No Encontrado'}) o Rol ({'Encontrado' if role else 'No Encontrado'})"
            )
            return

        try:
            # Insertar directamente en la tabla de asociación
            await db.execute(insert(UserRole).values(user_id=user.id, role_id=role.id))
            await db.commit()
            print("¡Rol VENDEDOR asignado correctamente!")
        except Exception as e:
            await db.rollback()
            print(f"Nota: El rol podría ya estar asignado o hubo un error: {e}")


if __name__ == "__main__":
    asyncio.run(grant_role())
