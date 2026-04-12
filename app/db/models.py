import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD

class Organization(Base):
    __tablename__ = "organizations"

    org_id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    domain = Column(Text, unique=True, nullable=False)
    max_domains = Column(Integer, default=1, nullable=False)


class Organization(Base):
    __tablename__ = "organizations"

    org_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    domain = Column(Text, nullable=False)
    max_domains = Column(Integer, default=1, nullable=False)


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True)
    org_id = Column(String(36), ForeignKey("organizations.org_id"), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    domain = Column(Text, nullable=False)
    role = Column(String(20), nullable=False, default="owner")
    organization_id = Column(String(36), ForeignKey("organizations.org_id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
=======
# class User(Base):
#     __tablename__ = "users"

#     user_id = Column(String(36), primary_key=True)
#     email = Column(String(255), unique=True, nullable=False)
#     password = Column(String(255), nullable=False)
#     domain = Column(Text, nullable=False)
#     created_at = Column(TIMESTAMP, server_default=func.now())
>>>>>>> f4a690b (Refactor scanner API routes and schemas; remove user_id dependency from scan tasks)


class Invitation(Base):
    __tablename__ = "invitations"

    invite_id = Column(String(36), primary_key=True)
    org_id = Column(String(36), ForeignKey("organizations.org_id"), nullable=False)
    email = Column(String(255), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    invited_by = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)


class PromoCode(Base):
    __tablename__ = "promo_codes"

    code_id = Column(String(36), primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    used_by_org = Column(String(36), ForeignKey("organizations.org_id"), nullable=True)
    used_at = Column(TIMESTAMP, nullable=True)

=======
=======

>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="owner")
    created_at = Column(TIMESTAMP, server_default=func.now())
>>>>>>> c2ee839 (Refactor fix API routes; remove user_id dependency from create_scan_task_to_queue and submit_fix functions)


class Invitation(Base):
    __tablename__ = "invitations"

    invite_id = Column(String(36), primary_key=True)
    email = Column(String(255), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    org_id = Column(String(36), ForeignKey("organizations.org_id"), nullable=False)
    invited_by = Column(String(36), ForeignKey("users.user_id"), nullable=False)


class PromoCode(Base):
    __tablename__ = "promo_codes"

    code_id = Column(String(36), primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(TIMESTAMP, nullable=True)
    used_by = Column(String(36), ForeignKey("users.user_id"), nullable=True)


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
<<<<<<< HEAD
<<<<<<< HEAD
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)

=======
>>>>>>> 95ca74d (invite members to org via email, org-wise history, promo code generateion, redeem code, smtp email added plus some minor changes)
=======
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
    summary = Column(JSONB, nullable=False)
    answers = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

<<<<<<< HEAD

# ── Scan ──────────────────────────────────────────────────────
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
=======
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)

class ScanResult(Base):
    __tablename__ = "scan_result"

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    scan_id = Column(String(36), ForeignKey("scan_request.scan_id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    domain = Column(Text, nullable=False)
=======
    scan_id = Column(String(36),ForeignKey("scan_request.scan_id", ondelete="CASCADE"), primary_key=True)
    # user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    domain = Column(Text, nullable=False) 
>>>>>>> f4a690b (Refactor scanner API routes and schemas; remove user_id dependency from scan tasks)
=======
    user_id = Column(String(36), ForeignKey("users.user_id"),primary_key=True, nullable=True)
=======
    org_id = Column(String(36), ForeignKey("organizations.org_id"), primary_key=True, nullable=False)
>>>>>>> f2b3fc1 (member feature plus some route changes)
    domain = Column(Text, nullable=False)
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
    results = Column(JSONB, nullable=False)
    time = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        Index("idx_scan_result_domain", "domain"),
    )


class ScanSummary(Base):
    __tablename__ = "scan_summary"

    domain = Column(Text, primary_key=True)
    org_id = Column(String(36), ForeignKey("organizations.org_id"), nullable=False)
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