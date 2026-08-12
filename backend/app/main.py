from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Real Estate AI Service API",
    description="API for generating professional real estate property descriptions.",
    version="1.0.0"
)

# Enable CORS so your decoupled frontend can safely communicate with this backend API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# The structural schema matching your frontend inputs exactly
class PropertyPayload(BaseModel):
    property_type: str = Field(..., min_length=2, description="Type of property, e.g. Detached Duplex")
    bedrooms: int = Field(..., ge=0, description="Number of bedrooms")
    location: str = Field(..., min_length=2, description="Property location")
    price: str = Field(..., min_length=1, description="Property price")
    unique_features: str = Field(..., min_length=2, description="Important property features")

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
async def generate_description(payload: PropertyPayload):
    # Mock generation engine that simulates our future AI output
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

    return {
        "success": True,
        "generated_text": generated_text
    }
