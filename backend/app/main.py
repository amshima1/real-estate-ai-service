from pathlib import Path
from fastapi import FastAPI, status, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Property

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Real Estate AI Service API",
    description="API for generating and saving professional real estate property descriptions.",
    version="1.0.0"
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PropertyPayload(BaseModel):
    property_type: str = Field(..., min_length=2)
    bedrooms: int = Field(..., ge=0)
    location: str = Field(..., min_length=2)
    price: str = Field(..., min_length=1)
    unique_features: str = Field(..., min_length=2)

    # Optional property visual views
    front_image: str | None = None
    back_image: str | None = None
    right_image: str | None = None
    left_image: str | None = None


@app.post("/upload-image", status_code=status.HTTP_200_OK)
async def upload_image(file: UploadFile = File(...)):
    allowed_types = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and WEBP images are allowed."
        )

    upload_dir = Path(__file__).resolve().parent.parent / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    import uuid

    extension = allowed_types[file.content_type]
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = upload_dir / filename

    contents = await file.read()

    max_size = 5 * 1024 * 1024

    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail="Image must be 5MB or smaller."
        )

    file_path.write_bytes(contents)

    return {
        "success": True,
        "filename": filename,
        "url": f"/uploads/{filename}"
    }


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {
        "status": "online",
        "service": "Real Estate AI Service API",
        "version": "1.0.0"
    }


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy"
    }


@app.post("/properties/generate", status_code=status.HTTP_200_OK)
async def generate_description(
    payload: PropertyPayload,
    db: Session = Depends(get_db)
):
    generated_text = (
        f"MARKETING LISTING COPY\n"
        f"=======================\n"
        f"Discover this premium, beautifully designed {payload.bedrooms}-bedroom "
        f"{payload.property_type} situated in the highly sought-after neighborhood of {payload.location}.\n\n"
        f"Market Valuation: {payload.price}\n\n"
        f"Property Highlights & Amenities:\n"
        f"• {payload.unique_features}\n\n"
        f"This exceptional property offers an unmatched living experience. "
        f"Contact our agency today to coordinate an exclusive private viewing layout."
    )

    property_record = Property(
        property_type=payload.property_type,
        bedrooms=payload.bedrooms,
        location=payload.location,
        price=payload.price,
        unique_features=payload.unique_features,
        generated_text=generated_text,
        front_image=payload.front_image,
        back_image=payload.back_image,
        right_image=payload.right_image,
        left_image=payload.left_image
    )

    db.add(property_record)
    db.commit()
    db.refresh(property_record)

    return {
        "success": True,
        "property_id": property_record.id,
        "generated_text": generated_text
    }


@app.get("/properties", status_code=status.HTTP_200_OK)
async def get_properties(db: Session = Depends(get_db)):
    properties = db.query(Property).order_by(Property.id.desc()).all()

    return {
        "success": True,
        "count": len(properties),
        "properties": [
            {
                "id": property.id,
                "property_type": property.property_type,
                "bedrooms": property.bedrooms,
                "location": property.location,
                "price": property.price,
                "unique_features": property.unique_features,
                "generated_text": property.generated_text,
                "front_image": property.front_image,
                "back_image": property.back_image,
                "right_image": property.right_image,
                "left_image": property.left_image,
                "created_at": property.created_at
            }
            for property in properties
        ]
    }


@app.get("/properties/{property_id}", status_code=status.HTTP_200_OK)
async def get_property(property_id: int, db: Session = Depends(get_db)):
    property_record = db.query(Property).filter(Property.id == property_id).first()

    if property_record is None:
        return {
            "success": False,
            "message": "Property not found"
        }

    # Record this property view
    property_record.view_count += 1
    db.commit()
    db.refresh(property_record)

    return {
        "success": True,
        "property": {
            "id": property_record.id,
            "property_type": property_record.property_type,
            "bedrooms": property_record.bedrooms,
            "location": property_record.location,
            "price": property_record.price,
            "unique_features": property_record.unique_features,
            "generated_text": property_record.generated_text,
            "front_image": property_record.front_image,
            "back_image": property_record.back_image,
            "right_image": property_record.right_image,
            "left_image": property_record.left_image,
            "created_at": property_record.created_at,
            "view_count": property_record.view_count
        }
    }

@app.delete("/properties/{property_id}", status_code=status.HTTP_200_OK)
async def delete_property(property_id: int, db: Session = Depends(get_db)):
    property_record = db.query(Property).filter(Property.id == property_id).first()

    if property_record is None:
        return {
            "success": False,
            "message": "Property not found"
        }

    db.delete(property_record)
    db.commit()

    return {
        "success": True,
        "message": "Property deleted successfully",
        "property_id": property_id
    }


@app.put("/properties/{property_id}", status_code=status.HTTP_200_OK)
async def update_property(
    property_id: int,
    payload: PropertyPayload,
    db: Session = Depends(get_db)
):
    property_record = db.query(Property).filter(Property.id == property_id).first()

    if property_record is None:
        return {
            "success": False,
            "message": "Property not found"
        }

    property_record.property_type = payload.property_type
    property_record.bedrooms = payload.bedrooms
    property_record.location = payload.location
    property_record.price = payload.price
    property_record.unique_features = payload.unique_features

    property_record.front_image = payload.front_image
    property_record.back_image = payload.back_image
    property_record.right_image = payload.right_image
    property_record.left_image = payload.left_image

    property_record.generated_text = (
        f"MARKETING LISTING COPY\n"
        f"=======================\n"
        f"Discover this premium, beautifully designed {payload.bedrooms}-bedroom "
        f"{payload.property_type} situated in the highly sought-after neighborhood of {payload.location}.\n\n"
        f"Market Valuation: {payload.price}\n\n"
        f"Property Highlights & Amenities:\n"
        f"• {payload.unique_features}\n\n"
        f"This exceptional property offers an unmatched living experience. "
        f"Contact our agency today to coordinate an exclusive private viewing layout."
    )

    db.commit()
    db.refresh(property_record)

    return {
        "success": True,
        "message": "Property updated successfully",
        "property_id": property_record.id,
        "generated_text": property_record.generated_text
    }
