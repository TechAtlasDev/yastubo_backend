---
title: Personalización del Calculador
description: Cómo ajustar la lógica de precios y reglas actuariales en el motor de cotización de Yastubo.
---

El motor de cálculo de Yastubo (`plans/calculator.py`) es el núcleo financiero de la plataforma. Permite definir reglas de precios flexibles basadas en edad, ubicación geográfica y tipos de cobertura, asegurando que cada póliza sea rentable y competitiva.

## Core Benefits / Key Features
* **Precisión Actuarial:** Control total sobre recargos y descuentos.
* **Flexibilidad por País:** Capacidad de sobreescribir precios base según el mercado local.
* **Transparencia Total:** Cada cálculo devuelve un desglose completo de los factores aplicados.
* **Fácil Extensión:** Añadir nuevas variables de riesgo sin afectar la estructura central.

## Deep Dive Técnico: Lógica del Motor de Precios

La lógica reside principalmente en la función `calculate_price` dentro de `app/modules/plans/calculator.py`.

### Desglose de la Fórmula de Cálculo

El sistema utiliza una fórmula acumulativa para determinar el precio final:

1. **Selección del Precio Base:** Si existe un `country_override`, se ignora el `base_price` global.
2. **Aplicación del Recargo por Edad:** Se busca el rango de edad correspondiente y se aplica el porcentaje de recargo.
3. **Cálculo de Unidad:** `Precio Base + (Precio Base * % Recargo)`.
4. **Cálculo Final:** `Precio de Unidad * Cantidad`.

```python
# Desglose matemático simplificado:
# Precio Unidad = Base * (1 + Surcharge_Percentage / 100)
# Precio Final = Precio Unidad * Cantidad
```

### Implementación Técnica

A continuación se muestra un ejemplo de cómo el motor procesa una cotización:

```python
from decimal import Decimal

# Ejemplo de estructura de rangos de edad
age_ranges = [
    {"min_age": 18, "max_age": 30, "surcharge_percentage": 5},  # +5% riesgo
    {"min_age": 31, "max_age": 50, "surcharge_percentage": 10}, # +10% riesgo
    {"min_age": 51, "max_age": 70, "surcharge_percentage": 25}  # +25% riesgo
]

# Invocación del motor
cotizacion = calculate_price(
    base_price=Decimal("100.00"),
    age=45,
    age_ranges=age_ranges,
    country_override=Decimal("110.00"), # Override por país: México
    quantity=2
)

# Resultado:
# effective_base: 110.00 (override)
# surcharge_amount: 110.00 * 10% = 11.00
# unit_price: 110.00 + 11.00 = 121.00
# final_price: 121.00 * 2 = 242.00
```

## Ejemplo Práctico: Añadir un "Descuento por Grupo"

Si deseas añadir un descuento especial cuando la cantidad es mayor a 5, puedes extender el servicio de la siguiente manera:

```python
# app/modules/plans/service.py

def apply_group_discount(price_data: dict) -> dict:
    if price_data["quantity"] >= 5:
        discount = price_data["final_price"] * Decimal("0.10") # 10% de descuento
        price_data["final_price"] -= discount
        price_data["applied_discounts"] = "GROUP_DISCOUNT_10"
    return price_data
```

:::tip[Redondeo]
Utilizamos siempre `quantize(Decimal("0.01"))` para asegurar que los cálculos monetarios no presenten errores de precisión de punto flotante.
:::

## Diagrama de Flujo de Cotización

![Customizing Calculator Flow](https://res.cloudinary.com/de1xmnmeq/image/upload/v1774844477/722b9e43-ea2e-483d-a49e-ab6ad403fe67.png)
