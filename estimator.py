"""Transparent illustrative cost model for a customer discovery demo.

Not a live AWS/Azure price quote. All unit costs are user-supplied assumptions.
"""
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Scenario:
    company: str
    users: int
    storage_tb: float
    current_storage_monthly: float
    current_admin_monthly: float
    proposed_storage_per_gb_month: float
    proposed_admin_monthly: float
    proposed_licenses_monthly: float
    one_time_migration: float
    contingency_pct: float = 15.0
    annual_growth_pct: float = 0.0


def evaluate(s: Scenario) -> dict:
    if s.users < 1 or s.storage_tb <= 0:
        raise ValueError('Users and storage must be positive')
    for field, value in asdict(s).items():
        if isinstance(value, (float, int)) and field not in ('annual_growth_pct',) and value < 0:
            raise ValueError(f'{field} cannot be negative')
    if not 0 <= s.contingency_pct <= 100 or not -99 <= s.annual_growth_pct <= 1000:
        raise ValueError('Growth or contingency percentage outside allowed range')
    current_monthly = s.current_storage_monthly + s.current_admin_monthly
    proposed_monthly = (s.storage_tb * 1024 * s.proposed_storage_per_gb_month
                        + s.proposed_admin_monthly + s.proposed_licenses_monthly)
    migration_with_contingency = s.one_time_migration * (1 + s.contingency_pct / 100)
    annual_current = current_monthly * 12
    annual_proposed = proposed_monthly * 12 + migration_with_contingency
    first_year_difference = annual_current - annual_proposed
    steady_monthly_savings = current_monthly - proposed_monthly
    payback_months = (migration_with_contingency / steady_monthly_savings
                      if steady_monthly_savings > 0 else None)
    # Year 2 assumes a steady % growth in stored data; other charges stay constant.
    next_storage_tb = s.storage_tb * (1 + s.annual_growth_pct / 100)
    year2_proposed = (next_storage_tb * 1024 * s.proposed_storage_per_gb_month
                      + s.proposed_admin_monthly + s.proposed_licenses_monthly) * 12
    return {
        'current_monthly': round(current_monthly, 2),
        'proposed_monthly': round(proposed_monthly, 2),
        'migration_with_contingency': round(migration_with_contingency, 2),
        'first_year_difference': round(first_year_difference, 2),
        'steady_monthly_savings': round(steady_monthly_savings, 2),
        'payback_months': round(payback_months, 1) if payback_months is not None else None,
        'year2_proposed_annual': round(year2_proposed, 2),
        'annual_current': round(annual_current, 2),
        'annual_proposed': round(annual_proposed, 2),
        'recommendation': (
            'Estimated savings after one-time migration expense in year one.'
            if first_year_difference > 0 else
            'Year-one costs exceed current costs; investigate broader benefits, scope, or pricing.'
        ),
    }
