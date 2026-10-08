from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.risk_engine import RiskEngine

router = APIRouter()

@router.get("/api/risk/overall")
def get_overall_risk(db: Session = Depends(get_db)):
    engine = RiskEngine(db)
    return engine.calculate_overall_risk()

@router.get("/api/risk/asset/{asset_id}")
def get_asset_risk(asset_id: int, db: Session = Depends(get_db)):
    from app.models.asset import Asset
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return {"error": "Asset not found"}
    engine = RiskEngine(db)
    return engine.calculate_asset_risk(asset)

@router.get("/api/risk/breakdown")
def get_risk_breakdown(db: Session = Depends(get_db)):
    engine = RiskEngine(db)
    return engine.get_risk_breakdown()

@router.get("/api/risk/all")
def get_all_asset_risks(db: Session = Depends(get_db)):
    engine = RiskEngine(db)
    assets = db.query(Asset).filter(Asset.is_active == True).all()
    return [engine.calculate_asset_risk(a) for a in assets]