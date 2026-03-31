---
title: Geography (Geografía Centralizada)
description: Gestión de países, zonas geográficas y asociaciones para la tarificación y emisión.
---

El módulo de **Geography** proporciona la infraestructura base para gestionar la ubicación física de los riesgos y la segmentación de mercados. Este módulo es el primero en migrarse al esquema real legado de Yastubo.

## Key Features

*   **Esquema Legado**: Sincronización 1:1 con las tablas `countries` y `zones` del sistema de producción anterior.
*   **Gestión Multi-Zona**: Capacidad de agrupar países en zonas (ej. "Latinoamérica", "Cono Sur", "Europa") para aplicar reglas de negocio grupales.
*   **Soporte Multi-Idioma**: Los nombres de los países se almacenan en formato JSON para soportar múltiples traducciones nativas.
*   **ISO Standard**: Uso de estándares ISO2 e ISO3 para la interoperabilidad con pasarelas de pago y proveedores externos.

:::tip[Migración]
Este módulo utiliza `BigInteger` para los IDs con el fin de mantener la compatibilidad con los registros existentes del backup SQL. A diferencia de otros módulos que usan UUID, este módulo está diseñado para importar datos masivos.
:::

## Deep Dive Técnico

### Estructura de Datos
El módulo se compone de tres entidades principales:
1.  **Country**: Información detallada del país, incluyendo códigos de continente y prefijos telefónicos.
2.  **Zone**: Agrupaciones lógicas de países.
3.  **CountryZone**: Tabla de asociación muchos-a-muchos con soporte para auditoría.

### Lógica de Asociación
Un país puede pertenecer a múltiples zonas simultáneamente. Esto es crucial para planes de asistencia que cubren regiones geográficas específicas que pueden solaparse.

## Ejemplo de Implementación

A continuación, un fragmento del modelo SQLAlchemy que define la estructura del país:

```python
class Country(GeographyBase):
    """Model representing a country as defined in the legacy schema."""
    __tablename__ = "countries"

    name: Mapped[dict] = mapped_column(JSON, nullable=False)
    iso2: Mapped[Optional[str]] = mapped_column(CHAR(2), unique=True, nullable=True)
    iso3: Mapped[Optional[str]] = mapped_column(CHAR(3), unique=True, nullable=True)
    continent_code: Mapped[str] = mapped_column(String(2), index=True, nullable=False)
    phone_code: Mapped[Optional[str]] = mapped_column(String(10), index=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    zones: Mapped[List["Zone"]] = relationship(
        secondary="country_zone", back_populates="countries"
    )
```

## Endpoints Principales

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/v1/geography/countries` | Lista de países disponibles. |
| `POST` | `/api/v1/geography/countries` | Registro de un nuevo país. |
| `GET` | `/api/v1/geography/zones` | Lista de zonas geográficas. |
| `POST` | `/api/v1/geography/zones/{z_id}/countries/{c_id}` | Asociar país a una zona. |

## Próximos Pasos
Este módulo servirá como base para la normalización del módulo de **Plans**, permitiendo que las coberturas y precios se definan por país o zona de manera relacional.
