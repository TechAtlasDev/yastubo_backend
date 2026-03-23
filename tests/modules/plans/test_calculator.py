import pytest
from decimal import Decimal
from app.modules.plans.calculator import calculate_price

def test_calculate_price_no_surcharge_age_range():
    age_ranges = [{"min_age": 0, "max_age": 30, "surcharge_percentage": 0}]
    res = calculate_price(Decimal("100.00"), 25, age_ranges, None)
    assert res["final_price"] == Decimal("100.00")
    assert res["age_surcharge_amount"] == Decimal("0.00")

def test_calculate_price_applies_age_surcharge_correctly():
    age_ranges = [{"min_age": 31, "max_age": 50, "surcharge_percentage": 15}]
    res = calculate_price(Decimal("100.00"), 40, age_ranges, None)
    assert res["final_price"] == Decimal("115.00")
    assert res["age_surcharge_amount"] == Decimal("15.00")

def test_calculate_price_uses_country_override_over_base_price():
    age_ranges = [{"min_age": 0, "max_age": 100, "surcharge_percentage": 10}]
    # Base 100, Override 200. Surcharge 10% of 200 = 20. Total 220.
    res = calculate_price(Decimal("100.00"), 30, age_ranges, Decimal("200.00"))
    assert res["effective_base"] == Decimal("200.00")
    assert res["final_price"] == Decimal("220.00")

def test_calculate_price_age_not_in_any_range_raises_error():
    age_ranges = [{"min_age": 0, "max_age": 30, "surcharge_percentage": 0}]
    with pytest.raises(ValueError, match="Age not covered by any range"):
        calculate_price(Decimal("100.00"), 35, age_ranges, None)

def test_calculate_price_with_quantity_multiplies_correctly():
    age_ranges = [{"min_age": 0, "max_age": 100, "surcharge_percentage": 0}]
    res = calculate_price(Decimal("100.00"), 25, age_ranges, None, quantity=3)
    assert res["final_price"] == Decimal("300.00")

def test_calculate_price_zero_surcharge_returns_base():
    age_ranges = [{"min_age": 0, "max_age": 100, "surcharge_percentage": 0}]
    res = calculate_price(Decimal("100.00"), 25, age_ranges, None)
    assert res["final_price"] == Decimal("100.00")
