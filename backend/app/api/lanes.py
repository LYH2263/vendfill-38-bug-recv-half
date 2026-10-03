from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Lane
from app.services.fill_engine import compute_gap
router = APIRouter(prefix="/lanes", tags=["lanes"])

@router.get("")
def list_lanes(location_id: int | None = None, db: Session = Depends(get_db)):
    q = select(Lane).order_by(Lane.slot_no)
    if location_id is not None: q = q.where(Lane.location_id == location_id)
    out = []
    for r in db.scalars(q).all():
        gap = compute_gap(r.capacity, r.stock, r.in_transit)
        out.append({"id": r.id, "location_id": r.location_id, "slot_no": r.slot_no, "sku_name": r.sku_name,
                    "capacity": r.capacity, "stock": r.stock, "in_transit": r.in_transit, "gap": gap,
                    "fill_pct": round(r.stock / r.capacity * 100, 1) if r.capacity else 0})
    return out
