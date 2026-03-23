from decimal import Decimal
from typing import List, Optional

def calculate_price(
    base_price: Decimal,
    age: int,
    age_ranges: List[dict],
    country_override: Optional[Decimal],
    quantity: int = 1
) -> dict:
    """
    Pure price calculation logic.
    age_ranges should be a list of dicts with min_age, max_age, surcharge_percentage.
    """
    effective_base = country_override if country_override is not None else base_price
    
    # Find applicable age range
    selected_range = None
    for r in age_ranges:
        if r["min_age"] <= age <= r["max_age"]:
            selected_range = r
            break
            
    if selected_range is None:
        raise ValueError("Age not covered by any range")
        
    surcharge_pct = Decimal(str(selected_range["surcharge_percentage"]))
    surcharge_amount = (effective_base * surcharge_pct / Decimal("100")).quantize(Decimal("0.01"))
    
    unit_price = effective_base + surcharge_amount
    final_price = (unit_price * Decimal(str(quantity))).quantize(Decimal("0.01"))
    
    return {
        "base_price": base_price,
        "effective_base": effective_base,
        "country_override": country_override,
        "age": age,
        "age_surcharge_percentage": surcharge_pct,
        "age_surcharge_amount": surcharge_amount,
        "unit_price": unit_price,
        "quantity": quantity,
        "final_price": final_price,
        "range_applied": f"{selected_range['min_age']}-{selected_range['max_age']}"
    }
