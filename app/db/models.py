import uuid
from sqlalchemy import Column, String, Text, Integer, ForeignKey, TIMESTAMP, Index, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

# class User(Base):
#     __tablename__ = "users"

#     user_id = Column(String(36), primary_key=True)
#     email = Column(String(255), unique=True, nullable=False)
#     password = Column(String(255), nullable=False)
#     domain = Column(Text, nullable=False)
#     created_at = Column(TIMESTAMP, server_default=func.now())

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

    summary = Column(JSONB, nullable=False)
    answers = Column(JSONB, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())

class ScanRequest(Base):
    __tablename__ = "scan_request"

    scan_id = Column(String(36), primary_key=True)
    # user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    domain = Column(Text, nullable=False)
    time = Column(TIMESTAMP, server_default=func.now())
    data = Column(JSONB, nullable=True)

    __table_args__ = (
        Index("idx_scan_request_domain", "domain"),
    )

class ScanResult(Base):
    __tablename__ = "scan_result"

    scan_id = Column(String(36),ForeignKey("scan_request.scan_id", ondelete="CASCADE"), primary_key=True)
    # user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    domain = Column(Text, nullable=False) 
    results = Column(JSONB, nullable=False)

    __table_args__ = (
        Index("idx_scan_result_domain", "domain"),
    )

class ScanSummary(Base):
    __tablename__ = "scan_summary"

    scan_id = Column(String, ForeignKey("scan_result.scan_id", ondelete="CASCADE"), primary_key=True)
    # user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    domain = Column(Text, nullable=False)
    domain_score = Column(Integer)
    severity = Column(String)
    mail_security = Column(JSONB, nullable=True)
    app_security = Column(JSONB, nullable=True)
    network_security = Column(JSONB, nullable=True)
    tls_security = Column(JSONB, nullable=True)
    dns_security = Column(JSONB, nullable=True)
    ips = Column(JSONB, nullable=True)

    __table_args__ = (
        Index("idx_scan_summary_score", "domain_score"),
    )