from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models, schemas, oauth2
from sqlalchemy import or_

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/images", response_model=List[schemas.imageOut])
def search_images(
    daytime: Optional[str] = None,
    weather: Optional[str] = None,
    indoor: Optional[bool] = None,
    primary_object: Optional[str] = None,
    limit: int = 20,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    base_filter = or_(models.Image.owner_id == current_user.id, models.Image.private == False)

    query = db.query(models.Image).filter(base_filter)

    if daytime:
        query = query.filter(models.Image.daytime.ilike(f"%{daytime}%"))

    if weather:
        query = query.filter(models.Image.weather.ilike(f"%{weather}%"))

    if indoor is not None:
        query = query.filter(models.Image.indoor == indoor)

    if primary_object:
        query = query.filter(models.Image.primary_object.ilike(f"%{primary_object}%"))

    images = (
        query.order_by(models.Image.created_at.desc()).offset(skip).limit(limit).all()
    )

    return images
