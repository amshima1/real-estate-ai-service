from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from .database import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    property_type = Column(String(100), nullable=False)
    bedrooms = Column(Integer, nullable=False)
    location = Column(String(255), nullable=False)
    price = Column(String(100), nullable=False)
    unique_features = Column(Text, nullable=False)
    generated_text = Column(Text, nullable=True)

    # Property visual views
    front_image = Column(String(500), nullable=True)
    back_image = Column(String(500), nullable=True)
    right_image = Column(String(500), nullable=True)
    left_image = Column(String(500), nullable=True)

    # Number of times visitors have viewed this property
    view_count = Column(Integer, nullable=False, default=0, server_default="0")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
