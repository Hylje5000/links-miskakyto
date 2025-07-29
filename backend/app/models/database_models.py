"""
SQLAlchemy database models for Alembic migrations.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Link(Base):
    """Link model matching our current database schema."""
    __tablename__ = "links"
    
    id = Column(String, primary_key=True)  # Use String for shortuuid
    original_url = Column(Text, nullable=False)
    short_code = Column(String, unique=True, nullable=False)
    description = Column(Text)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.current_timestamp())
    created_by = Column(String)
    created_by_name = Column(String)
    tenant_id = Column(String)
    
    # Relationship to clicks
    clicks = relationship("Click", back_populates="link", cascade="all, delete-orphan")


class Click(Base):
    """Click tracking model."""
    __tablename__ = "clicks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    link_id = Column(String, ForeignKey("links.id", ondelete="CASCADE"), nullable=False)  # String to match Link.id
    clicked_at = Column(DateTime, default=func.current_timestamp())
    ip_address = Column(String)
    user_agent = Column(Text)
    
    # Relationship to link
    link = relationship("Link", back_populates="clicks")
