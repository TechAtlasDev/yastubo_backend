---
title: Plans (Lógica Actuarial)
description: Configuración de productos, gestión de coberturas y motor de cálculo de precios.
---

El módulo de **Plans** es el motor financiero de Yastubo. Define qué productos están disponibles, en qué países, y cómo se calculan las primas de seguros basadas en factores de riesgo como la edad del asegurado.

## Key Features

*   **Actuarial Calculator**: Motor de cálculo dinámico que aplica recargos por rangos de edad y sobrecostos por país.
*   **Versionamiento de Planes**: Cada cambio en un plan genera una nueva versión con un "snapshot" de las condiciones en ese momento.
*   **Vesting Periods (Carencias)**: Control granular de días de espera para coberturas por causas naturales, accidentales o suicidio.
*   **Geofencing**: Disponibilidad de planes y overrides de precios específicos por código de país (ISO).

:::note[Importante]
Las pólizas emitidas se vinculan a una versión específica de un plan. Esto garantiza que, si las tarifas cambian en el futuro, los contratos existentes mantengan sus condiciones originales.
:::

## Deep Dive Técnico

### Lógica de Cálculo de Precios
El sistema desglosa el precio final siguiendo un flujo secuencial:

1.  **Precio Base**: Se toma el `base_price` definido en el plan o el `base_price_override` si el país del asegurado tiene una configuración específica.
2.  **Recargo por Edad**: Se identifica el rango de edad aplicable (`AgeRange`) y se calcula el monto proporcional del recargo.
3.  **Fórmula Matemática**:
    $$P_{final} = (P_{base} + (P_{base} \times \%_{recargo\_edad})) \times Q$$
    Donde $P$ es precio y $Q$ es cantidad.

### Estructura de Datos
*   **Plan**: El modelo raíz que contiene la configuración general.
*   **AgeRange**: Define los límites de edad y el porcentaje de recargo (ej. 18-30 años -> 0%, 65-70 años -> 50%).
*   **CountryConfig**: Define en qué países opera el plan y si existe un precio base diferencial.
*   **Coverage**: Catálogo maestro de coberturas que se asocian a los planes.

## Ejemplo Práctico: El Motor de Cálculo

El siguiente fragmento muestra la lógica pura de cálculo que reside en el núcleo del sistema:

```python
def calculate_price(
    base_price: Decimal,
    age: int,
    age_ranges: List[dict],
    country_override: Optional[Decimal],
    quantity: int = 1,
) -> dict:
    """
    Lógica pura de cálculo de precios.
    Calcula el precio unitario aplicando recargos por edad y país.
    """
    # 1. Determinar el precio base efectivo (con o sin override de país)
    effective_base = country_override if country_override is not None else base_price

    # 2. Buscar el rango de edad aplicable al asegurado
    selected_range = None
    for r in age_ranges:
        if r["min_age"] <= age <= r["max_age"]:
            selected_range = r
            break

    if selected_range is None:
        raise ValueError("La edad no está cubierta por ningún rango configurado")

    # 3. Calcular el recargo por edad
    surcharge_pct = Decimal(str(selected_range["surcharge_percentage"]))
    surcharge_amount = (effective_base * surcharge_pct / Decimal("100")).quantize(
        Decimal("0.01")
    )

    # 4. Calcular el precio final según la cantidad
    unit_price = effective_base + surcharge_amount
    final_price = (unit_price * Decimal(str(quantity))).quantize(Decimal("0.01"))

    return {
        "final_price": final_price,
        "age_surcharge_amount": surcharge_amount,
        "unit_price": unit_price
    }
```

## Diagrama de Proceso

![Plans Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774844830/f44b2000-df26-4a03-bcc4-74bb488fd7f7.png)

## Endpoints Principales

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/v1/plans` | Lista de planes disponibles y activos. |
| `POST` | `/api/v1/plans/calculate-price` | Simulación de precios según edad y país. |
| `POST` | `/api/v1/plans/admin/create` | Creación de nuevos productos (Solo ADMIN). |
| `GET` | `/api/v1/plans/{id}` | Detalle completo de un plan, incluyendo versiones. |
