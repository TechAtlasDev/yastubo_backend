---
title: Creación de un Nuevo Módulo
description: Guía paso a paso para extender el backend de Yastubo con nuevas funcionalidades siguiendo la arquitectura modular.
---

# Creación de un Nuevo Módulo

Yastubo Backend está diseñado bajo una arquitectura modular estricta. Cada funcionalidad de negocio (ej. Seguros, IA, Pagos) reside en su propio espacio dentro de `app/modules`. Esta guía explica cómo crear un nuevo módulo desde cero siguiendo los estándares del proyecto.

## Core Benefits / Key Features
* **Aislamiento de Dominio:** Los cambios en un módulo no afectan lateralmente a otros.
* **Escalabilidad Horizontal:** Facilita la división del sistema en microservicios si fuera necesario en el futuro.
* **Testing Granular:** Cada módulo tiene su propio set de pruebas unitarias e integración.
* **Consistencia:** Todos los módulos siguen el mismo patrón de diseño (Service-Repository-Schema).

## Deep Dive Técnico: Estructura de un Módulo

Un módulo estándar debe contener los siguientes archivos:

1. `models.py`: Definiciones de tablas de base de datos (SQLAlchemy).
2. `schemas.py`: Modelos de validación de datos (Pydantic) para entrada y salida de API.
3. `service.py`: Capa de lógica de negocio (donde ocurre la "magia").
4. `router.py`: Definición de endpoints y orquestación de servicios.
5. `__init__.py`: Exportación selectiva de componentes clave.

### 1. Definición del Modelo (`models.py`)
Heredamos de `Base` para asegurar que las migraciones de Alembic detecten los cambios.

```python
from sqlalchemy import Column, String, Integer, ForeignKey
from app.shared.base_model import Base, TimestampMixin

class NewFeature(Base, TimestampMixin):
    __tablename__ = "new_features"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
```

### 2. Capa de Servicio (`service.py`)
Aquí es donde se implementan las reglas de negocio. Evita poner lógica compleja directamente en el router.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from .models import NewFeature
from .schemas import FeatureCreate

async def create_feature(db: AsyncSession, data: FeatureCreate, workspace_id: int):
    # Lógica de negocio aquí
    obj = NewFeature(**data.model_dump(), workspace_id=workspace_id)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj
```

## Ejemplo Práctico: Registro del Módulo

Una vez creado el módulo en `app/modules/mi_modulo`, debemos registrarlo en el router principal de la aplicación en `app/main.py`.

```python
# app/main.py

from app.modules.mi_modulo.router import router as mi_modulo_router

# ... dentro de la configuración de api_v1_router
api_v1_router.include_router(mi_modulo_router)
```

:::caution[Migraciones]
No olvides generar la migración de base de datos después de añadir nuevos modelos:
`uv run alembic revision --autogenerate -m "add mi_modulo table"`
:::

## Diagrama de Proceso de Extensión

![Creating New Module Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774844421/6a2c33d9-082b-4f24-a6a8-4a1a08e488b7.png)
