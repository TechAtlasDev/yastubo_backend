import asyncio
from app.core.database import engine
from app.shared.base_model import BaseModel

# Importamos todos los modelos para que el metadata los reconozca


async def sync_db_metadata():
    print("🛠️ Sincronizando esquema de DB mediante Metadata...")
    async with engine.begin() as conn:
        # Esto creará las columnas faltantes y tablas que no existan
        await conn.run_sync(BaseModel.metadata.create_all)
    print("✅ Esquema sincronizado.")


if __name__ == "__main__":
    asyncio.run(sync_db_metadata())
