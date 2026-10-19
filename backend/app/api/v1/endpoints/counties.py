import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.spatial import CountyDB

router = APIRouter()

@router.get("")
def get_all_counties(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    counties = db.query(CountyDB).order_by(CountyDB.code.asc()).all()
    results = []
    for c in counties:
        results.append({
            "code": c.code,
            "iso_code": c.iso_code,
            "name": c.name,
            "capital": c.capital,
            "population_2019": c.population_2019,
            "area_sq_km": c.area_sq_km,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "poverty_quintiles": {
                "q1": c.q1_pct,
                "q2": c.q2_pct,
                "q3": c.q3_pct,
                "q4": c.q4_pct,
                "q5": c.q5_pct
            } if c.q1_pct is not None else None,
            "icu_beds_verified": c.icu_beds_verified,
            "icu_source": c.icu_source,
            "data_quality_flags": json.loads(c.data_quality_flags) if c.data_quality_flags else []
        })
    return results
