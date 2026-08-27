from __future__ import annotations

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import BillingPlan, get_config
from app.core.database import get_async_session
from app.core.security import TokenPayload, require_admin
from app.models.postgres import Organization as OrganizationModel

logger = logging.getLogger("snt_ai.routers.billing")

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/stripe-webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
) -> dict:
    config = get_config()
    payload_bytes = await request.body()
    payload = json.loads(payload_bytes)
    sig_header = request.headers.get("stripe-signature", "")

    if config.environment.value != "development":
        secret = config.encryption_key or ""
        expected_sig = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, sig_header):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    event_type = payload.get("type", "")
    event_data = payload.get("data", {}).get("object", {})

    logger.info("Stripe webhook received: type=%s", event_type)

    if event_type == "customer.subscription.updated":
        customer_id = event_data.get("customer", "")
        new_plan = _map_stripe_plan(event_data.get("items", {}).get("data", [{}])[0].get("price", {}).get("lookup_key", ""))
        logger.info("Subscription updated: customer=%s plan=%s", customer_id, new_plan)
        if customer_id:
            result = await db.execute(select(OrganizationModel).where(OrganizationModel.stripe_customer_id == customer_id))
            org = result.scalar_one_or_none()
            if org:
                org.billing_plan = BillingPlan(new_plan)
                db.add(org)
                await db.commit()
            else:
                org_id = event_data.get("metadata", {}).get("org_id")
                if org_id:
                    result = await db.execute(select(OrganizationModel).where(OrganizationModel.id == org_id))
                    org = result.scalar_one_or_none()
                    if org:
                        org.stripe_customer_id = customer_id
                        org.billing_plan = BillingPlan(new_plan)
                        db.add(org)
                        await db.commit()

    elif event_type == "customer.subscription.deleted":
        customer_id = event_data.get("customer", "")
        logger.info("Subscription cancelled: customer=%s", customer_id)
        if customer_id:
            result = await db.execute(select(OrganizationModel).where(OrganizationModel.stripe_customer_id == customer_id))
            org = result.scalar_one_or_none()
            if org:
                org.billing_plan = BillingPlan.FREE
                db.add(org)
                await db.commit()

    elif event_type == "invoice.paid":
        customer_id = event_data.get("customer", "")
        amount = event_data.get("amount_paid", 0)
        logger.info("Invoice paid: customer=%s amount=%d", customer_id, amount)

    return {"received": True, "type": event_type}


@router.post("/stripe/portal")
async def create_portal_session(
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> dict:
    result = await db.execute(
        select(OrganizationModel).where(OrganizationModel.id == payload.org_id)
    )
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return {
        "url": f"https://billing.snt.ai/portal?org={payload.org_id}",
        "return_url": "https://app.snt.ai/settings/billing",
    }


def _map_stripe_plan(lookup_key: str) -> str:
    mapping = {
        "snt_free": BillingPlan.FREE.value,
        "snt_pro": BillingPlan.PRO.value,
        "snt_enterprise": BillingPlan.ENTERPRISE.value,
    }
    return mapping.get(lookup_key, BillingPlan.FREE.value)
