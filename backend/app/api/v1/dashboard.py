from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns dashboard revenue summary for a property.
    Enforces strict tenant isolation.
    """

    tenant_id = getattr(current_user, "tenant_id", None)

    # Prevent shared fallback tenant usage
    if not tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Tenant resolution failed"
        )

    revenue_data = await get_revenue_summary(
        property_id=property_id,
        tenant_id=tenant_id
    )

    # Financial-safe rounding
    total_revenue = round(
        float(revenue_data["total"]),
        2
    )

    return {
        "property_id": revenue_data["property_id"],
        "total_revenue": total_revenue,
        "currency": revenue_data["currency"],
        "reservations_count": revenue_data["count"]
    }