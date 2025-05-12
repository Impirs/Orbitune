from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.crud import get_connected_services

router = APIRouter(prefix="/connected_services", tags=["connected-services"])

@router.get("")
def list_connected_services(user_id: int, db: Session = Depends(get_db)):
    services = get_connected_services(db, user_id)
    return services

# Здесь можно добавить эндпоинты для удаления/обновления сервисов
