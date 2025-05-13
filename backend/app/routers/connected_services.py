from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.crud import get_connected_services
from app.models.models import ConnectedService  # Импортируем модель ConnectedService

router = APIRouter(prefix="/connected_services", tags=["connected-services"])

@router.get("")
def list_connected_services(user_id: int, db: Session = Depends(get_db)):
    services = get_connected_services(db, user_id)
    return [
        {
            "id": s.id,
            "platform": s.platform,
            "external_user_id": s.external_user_id,
            "is_connected": True,
            "expires_at": s.expires_at,
            # можно добавить другие поля
        }
        for s in services
    ]

@router.delete("")
def disconnect_service(user_id: int, platform: str, db: Session = Depends(get_db)):
    service = db.query(ConnectedService).filter_by(user_id=user_id, platform=platform).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()
    return {"ok": True}
