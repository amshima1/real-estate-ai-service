from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Property

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Real Estate AI Service API",
    description="API for generating and saving professional real estate property descriptions.",
    version="1.0.0"
)

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
        generated_text=generated_text
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
            "created_at": property_record.created_at
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
