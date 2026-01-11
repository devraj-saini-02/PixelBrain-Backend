import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import base64
import requests
import numpy as np
import cv2
import tempfile
import os

from typing import List, Dict, Optional
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi import Response, status, HTTPException, Depends, APIRouter

from app.database import get_db
from app import models, schemas, utils, oauth2

load_dotenv()

cloudinary.config( 
    cloud_name = os.getenv("CLOUD_NAME"),
    api_key = os.getenv("API_KEY"), 
    api_secret = os.getenv("API_SECRET_CLOUDINARY"),
    secure=True
)

pixelbrain=os.getenv("PIXELBRAIN")

router = APIRouter(prefix="/images",tags=['Images'])

from fastapi import UploadFile, File, Form

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.imageOut)
async def create_img(
    image: UploadFile = File(...),
    user_prompt: str = Form(None),
    dimensions: str = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    raw_bytes = await image.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Empty image file")
    files = {
        "image": (image.filename, raw_bytes, image.content_type)
    }
    data = {
        "text": user_prompt or ""
    }

    hf_response = requests.post(pixelbrain,files=files,data=data,timeout=90)

    if hf_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Processing API failed")

    result = hf_response.json()

    if result.get("status") != "success":
        raise HTTPException(status_code=500, detail="Image processing failed")

    processed_base64 = result["data"]["image_base64"]
    classification = result["data"]["classification"]
    detections = result["data"]["detection"]
    filters = result["data"]["applied_filters"]

    processed_bytes = base64.b64decode(processed_base64)
    nparr = np.frombuffer(processed_bytes, np.uint8)
    processed_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if processed_img is None:
        raise HTTPException(status_code=500, detail="Invalid processed image")

    success, encoded = cv2.imencode(".png", processed_img)
    if not success:
        raise HTTPException(status_code=500, detail="Encoding failed")

    upload_options = { "folder": "images","resource_type": "image"}

    if dimensions:
        try:
            obj_w, obj_h = map(int, dimensions.split(","))
            if obj_w > 0 and obj_h > 0:
                aspect_ratio = round(obj_w / obj_h, 4)
                upload_options["transformation"] = [
                    {
                        "aspect_ratio": aspect_ratio,
                        "crop": "fill",
                        "gravity": "auto"
                    }
                ]
        except:
            raise HTTPException(status_code=400, detail="Invalid dimensions format. Use 'width,height'")



    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(encoded.tobytes())
        tmp_path = tmp.name
    
    upload_result = cloudinary.uploader.upload(
        tmp_path,
        **upload_options
    )

    image_url = upload_result["secure_url"]
    public_id = upload_result["public_id"]
    
    os.remove(tmp_path)

    scene_type, _, time_of_day, weather_type = classification
    
    indoor = scene_type.lower() == "indoor"
    
    daytime = None
    weather = None
    
    if time_of_day.lower() != "not detected":
        daytime = time_of_day
    
    if weather_type.lower() != "not detected":
        weather = weather_type

    primary_object = None
    max_area = 0
    
    for label, boxes in detections.items():
        for bbox in boxes:
            x, y, w, h = bbox
            area = w * h
    
            if area > max_area:
                max_area = area
                primary_object = label

    new_image = models.Image(
        indoor=indoor,
        daytime=daytime,
        weather=weather,
        image_url=image_url,
        public_id=public_id,
        private=True,
        primary_object=primary_object,
        filter1=filters[1],
        filter2=filters[2] ,
        owner_id=current_user.id
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return new_image

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    image_query = db.query(models.Image).filter(models.Image.id == id)
    image = image_query.first()

    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    if image.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this image")

    try:
        destroy_result = cloudinary.uploader.destroy(image.public_id,invalidate=True)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete image from cloud storage")

    if not (destroy_result and destroy_result.get("result") in ("ok", "not_found", "deleted")):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cloudinary deletion failed")

    image_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}/private", response_model=schemas.imageOut)
def update_image_privacy(id: int, payload: schemas.PrivateUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    image_query = db.query(models.Image).filter(models.Image.id == id)
    image = image_query.first()

    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    if image.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this image")

    image.private = payload.private
    db.add(image)
    db.commit()
    db.refresh(image)

    return image


def delete_images_for_user(user_id: int, db: Session, delete_db_records: bool = False) -> Dict:
    images = db.query(models.Image).filter(models.Image.owner_id == user_id).all()

    total = len(images)
    cloud_deleted = 0
    db_deleted = 0
    failures: List[str] = []

    for img in images:
        try:
            res = cloudinary.uploader.destroy(img.public_id, resource_type='image')
        except Exception:
            failures.append(img.public_id)
            continue

        if res and res.get("result") in ("ok", "deleted", "not_found"):
            cloud_deleted += 1
            if delete_db_records:
                db.query(models.Image).filter(models.Image.id == img.id).delete(synchronize_session=False)
                db.commit()
                db_deleted += 1
        else:
            failures.append(img.public_id)

    return {"total": total, "cloud_deleted": cloud_deleted, "db_deleted": db_deleted, "failures": failures}


def get_images_for_user(user_id: int, db: Session, requester_id: Optional[int] = None, limit: int = 100, skip: int = 0) -> Dict:
    query = db.query(models.Image).filter(models.Image.owner_id == user_id)

    if requester_id is None or requester_id != user_id:
        query = query.filter(models.Image.private == False)

    total = query.count()

    imgs = query.order_by(models.Image.created_at.desc()).offset(skip).limit(limit).all()

    images: List[Dict] = []
    for img in imgs:
        images.append({
            "id": img.id,
            "image_url": img.image_url,
            "public_id": img.public_id,
            "private": bool(img.private),
            "created_at": img.created_at.isoformat() if img.created_at is not None else None,
            "indoor": bool(img.indoor),
            "daytime": img.daytime,
            "weather": img.weather,
            "primary_object": img.primary_object,
            "filter1": img.filter1,
            "filter2": img.filter2,
            "owner_id": img.owner_id,
        })

    return {"total": total, "images": images}



