from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Real Estate AI Service API",
    description="API for generating professional real estate property descriptions.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PropertyPayload(BaseModel):
    property_type: str = Field(
        ...,
        min_length=2,
        description="Type of property, e.g. Detached Duplex"
    )
    bedrooms: int = Field(
        ...,
        ge=0,
        description="Number of bedrooms"
    )
    location: str = Field(
        ...,
        min_length=2,
        description="Property location"
    )
    price: str = Field(
        ...,
        min_length=1,
        description="Property price"
    )
    unique_features: str = Field(
        ...,
        min_length=2,
        description="Important property features"
    )


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


@app.post("/generate-description", status_code=status.HTTP_200_OK)
async def generate_description(payload: PropertyPayload):

    generated_text = (
        f"Discover this beautiful {payload.bedrooms}-bedroom "
        f"{payload.property_type} in {payload.location}. "
        f"Priced at {payload.price}, this property offers "
        f"{payload.unique_features}. "
        f"Contact us today to schedule a viewing."
    )

    return {
        "success": True,
        "generated_text": generated_text
    }
