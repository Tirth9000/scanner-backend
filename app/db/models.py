import uuid
from sqlalchemy import Column, String, Text, Integer, ForeignKey, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Question(Base):
    __tablename__ = "questions"

    _id = Column(Integer, primary_key=True)
    category_id = Column(Integer, nullable=False)
    category_name = Column(Text, nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSONB, nullable=False)

class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    summary = Column(JSONB, nullable=False)
    category_scores = Column(JSONB, nullable=False)
    answers = Column(JSONB, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        Index("idx_assessment_results_user_id", "user_id"),
    )

class ScanResult(Base):
    __tablename__ = "scan_results"

    scan_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    domain = Column(Text, nullable=False)
    results = Column(JSONB, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        Index("idx_scan_results_user_id", "user_id"),
    )