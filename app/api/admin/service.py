import random
import string
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Blacklist, Organization, PromoCode, ScanScoreHistory, ScanSummary, User


def _generate_promo_string(length: int = 10) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


def _normalize_email(email: str) -> str:
    return email.lower().strip()


def _serialize_user(user: User, blocked_emails: set[str]) -> dict:
    return {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "is_blacklisted": user.email.lower() in blocked_emails,
    }


def generate_promo_code(db: Session) -> dict:
    code_str = _generate_promo_string()

    while db.query(PromoCode).filter(PromoCode.code == code_str).first():
        code_str = _generate_promo_string()

    promo = PromoCode(
        code_id=str(uuid.uuid4()),
        code=code_str,
        is_used=False,
    )

    db.add(promo)
    db.commit()
    db.refresh(promo)

    return {
        "message": "Promo code generated successfully",
        "code": promo.code,
    }


def get_promo_codes(db: Session) -> list[dict]:
    codes = db.query(PromoCode).all()
    used_by_ids = {code.used_by for code in codes if code.used_by}

    users_by_id = {}
    if used_by_ids:
        users_by_id = {
            user.user_id: user
            for user in db.query(User).filter(User.user_id.in_(used_by_ids)).all()
        }

    org_ids = {user.org_id for user in users_by_id.values() if user.org_id}
    orgs_by_id = {}
    if org_ids:
        orgs_by_id = {
            org.org_id: org
            for org in db.query(Organization).filter(Organization.org_id.in_(org_ids)).all()
        }

    owner_ids = {org.user_id for org in orgs_by_id.values() if org.user_id}
    owners_by_id = {}
    if owner_ids:
        owners_by_id = {
            owner.user_id: owner
            for owner in db.query(User).filter(User.user_id.in_(owner_ids)).all()
        }

    return [
        {
            "code": code.code,
            "is_used": code.is_used,
            "used_at": code.used_at.isoformat() if code.used_at else None,
            "used_by": (
                owners_by_id.get(orgs_by_id.get(user.org_id).user_id).email
                if code.used_by
                and (user := users_by_id.get(code.used_by))
                and user.org_id in orgs_by_id
                and orgs_by_id[user.org_id].user_id in owners_by_id
                else None
            ),
        }
        for code in codes
    ]


def get_users_by_org(db: Session) -> dict:
    organizations = db.query(Organization).order_by(Organization.domain.asc()).all()
    users = db.query(User).order_by(User.created_at.desc()).all()
    blocked_emails = {blocked.email for blocked in db.query(Blacklist).all()}

    users_by_org: dict[str, list[User]] = {}
    unassigned_users = []
    for user in users:
        if user.org_id:
            users_by_org.setdefault(user.org_id, []).append(user)
        else:
            unassigned_users.append(user)

    return {
        "organizations": [
            {
                "org_id": org.org_id,
                "domain": org.domain,
                "max_domains": org.max_domains,
                "users": [
                    _serialize_user(user, blocked_emails)
                    for user in users_by_org.get(org.org_id, [])
                ],
            }
            for org in organizations
        ],
        "admin": [
            _serialize_user(user, blocked_emails)
            for user in unassigned_users
        ],
    }


def block_email(email: str, current_admin: User, db: Session) -> dict:
    normalized_email = _normalize_email(email)

    if normalized_email == current_admin.email.lower():
        raise HTTPException(status_code=400, detail="Admin cannot block their own email")

    existing = db.query(Blacklist).filter(Blacklist.email == normalized_email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email is already blocked")

    blocked_user = Blacklist(
        email=normalized_email,
        blocked_by=current_admin.user_id,
    )
    db.add(blocked_user)
    db.commit()
    db.refresh(blocked_user)

    return {
        "message": "Email blocked successfully",
        "email": blocked_user.email,
        "blocked_by": blocked_user.blocked_by,
        "created_at": blocked_user.created_at.isoformat() if blocked_user.created_at else None,
    }


def unblock_email(email: str, db: Session) -> dict:
    normalized_email = _normalize_email(email)

    deleted_count = (
        db.query(Blacklist)
        .filter(Blacklist.email == normalized_email)
        .delete(synchronize_session=False)
    )

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Email is not blocked")

    db.commit()

    return {
        "message": "Email unblocked successfully",
        "email": normalized_email,
    }


def get_blacklisted_emails(db: Session) -> list[dict]:
    blocked_users = db.query(Blacklist).order_by(Blacklist.created_at.desc()).all()

    return [
        {
            "email": blocked_user.email,
            "blocked_by": blocked_user.blocked_by,
            "created_at": blocked_user.created_at.isoformat() if blocked_user.created_at else None,
        }
        for blocked_user in blocked_users
    ]


def get_scan_summaries(db: Session) -> list[dict]:
    summaries = db.query(ScanSummary).all()
    org_ids = {summary.org_id for summary in summaries}

    organizations = {}
    if org_ids:
        organizations = {
            org.org_id: org
            for org in db.query(Organization).filter(Organization.org_id.in_(org_ids)).all()
        }

    owner_ids = {org.user_id for org in organizations.values()}
    owners = {}
    if owner_ids:
        owners = {
            user.user_id: user
            for user in db.query(User).filter(User.user_id.in_(owner_ids)).all()
        }

    return [
        {
            "org_id": summary.org_id,
            "organization_domain": organizations.get(summary.org_id).domain
            if organizations.get(summary.org_id) else None,
            "owner_email": owners.get(organizations[summary.org_id].user_id).email
            if summary.org_id in organizations and organizations[summary.org_id].user_id in owners else None,
            "domain": summary.domain,
            "domain_score": summary.domain_score,
            "severity": summary.severity,
            "mail_security": summary.mail_security or {},
            "app_security": summary.app_security or {},
            "network_security": summary.network_security or {},
            "tls_security": summary.tls_security or {},
            "dns_security": summary.dns_security or {},
            "ips": summary.ips or [],
        }
        for summary in summaries
    ]


def get_total_scans(db: Session) -> dict:
    total_scans = db.query(ScanScoreHistory).count()
    return {"total_scans": total_scans}
