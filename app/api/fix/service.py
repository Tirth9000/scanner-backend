from collections import defaultdict
from sqlalchemy.orm import Session

from app.db.models import ScanSummary, ScanResult
from app.api.analyzer.controller import get_cvss_severity


FIX_TYPE_TO_ISSUE_KEY = {
    # Network Security
    "unexpected_port": "Unexpected open port",
    "risky_port":      "Risky port exposed",
    # Application Security
    "missing_csp":        "Missing CSP header",
    "missing_hsts":       "Missing HSTS header",
    "missing_x_frame":    "Missing X-Frame-Options",
    "missing_x_content":  "Missing X-Content-Type-Options",
    "http_without_https": "HTTP without HTTPS",
    # TLS Security
    "expired_tls":     "Expired TLS",
    "weak_tls":        "Weak TLS version",
    "tls_missing_443": "443 open without TLS",
    # DNS Security
    "missing_ns":    "Missing NS record",
    "missing_mx":    "Missing MX record",
    "missing_txt":   "Missing TXT record",
    "duplicate_spf": "Duplicate SPF record",
    "weak_spf":      "Weak SPF policy",
    "missing_spf":   "Missing SPF record",
    "missing_dmarc": "Missing DMARC",
    "weak_dmarc":    "Weak DMARC policy",
    "missing_dkim":  "Missing DKIM",
}

FIX_TYPE_TO_CATEGORY = {
    # Network Security
    "unexpected_port": "network_security",
    "risky_port":      "network_security",
    # Application Security
    "missing_csp":        "app_security",
    "missing_hsts":       "app_security",
    "missing_x_frame":    "app_security",
    "missing_x_content":  "app_security",
    "http_without_https": "app_security",
    # TLS Security
    "expired_tls":     "tls_security",
    "weak_tls":        "tls_security",
    "tls_missing_443": "tls_security",
    # DNS Security
    "missing_ns":    "dns_security",
    "missing_mx":    "dns_security",
    "missing_txt":   "dns_security",
    "duplicate_spf": "dns_security",
    "weak_spf":      "dns_security",
    "missing_spf":   "dns_security",
    "missing_dmarc": "dns_security",
    "weak_dmarc":    "dns_security",
    "missing_dkim":  "dns_security",
}

ISSUE_KEY_TO_PENALTY = {
    # DNS
    "Missing NS record":  2,
    "Missing MX record":  2,
    "Missing TXT record": 1,
    # Application
    "HTTP without HTTPS":          20,
    "Missing CSP header":           3,
    "Missing HSTS header":          4,
    "Missing X-Frame-Options":      2,
    "Missing X-Content-Type-Options": 2,
    # Network
    "Risky port exposed":   10,
    "Unexpected open port":  8,
    # TLS
    "443 open without TLS": 20,
    "Expired TLS":          20,
    "Weak TLS version":     15,
}

ALLOWED_CATEGORIES = {"app_security", "network_security", "tls_security", "dns_security"}


def is_fix_successful(result) -> bool:
    if isinstance(result, dict):
        for key in ("success", "is_success", "fixed"):
            if key in result:
                return bool(result[key])
        status = str(result.get("status", "")).strip().lower()
        if status:
            return status in {"success", "succeeded", "ok"}
    return False


def remove_fixed_issue(summary: ScanSummary, issue_key: str, domain: str, category: str) -> bool:
    if category not in ALLOWED_CATEGORIES:
        return False

    category_data = dict(getattr(summary, category) or {})
    findings = list(category_data.get(issue_key, []))
    if not findings:
        return False

    updated = [f for f in findings if f.get("subdomain") != domain]
    if len(updated) == len(findings):
        return False

    if updated:
        category_data[issue_key] = updated
    else:
        category_data.pop(issue_key, None)

    setattr(summary, category, category_data or None)
    return True


def recalculate_score(summary: ScanSummary, scan_result: ScanResult):
    subdomain_penalty: dict[str, int] = defaultdict(int)

    category_blocks = [
        summary.app_security     or {},
        summary.network_security or {},
        summary.tls_security     or {},
        summary.dns_security     or {},
    ]

    for block in category_blocks:
        for issue_key, findings in block.items():
            penalty = ISSUE_KEY_TO_PENALTY.get(issue_key, 0)
            if not penalty:
                continue
            for finding in findings or []:
                subdomain = finding.get("subdomain")
                if subdomain:
                    subdomain_penalty[subdomain] += penalty

    raw_subdomains = (
        (scan_result.results or {})
        .get("data", {})
        .get("subdomains", [])
    )
    subdomain_names = [s.get("subdomain") for s in raw_subdomains if s.get("subdomain")]
    if not subdomain_names:
        subdomain_names = list(subdomain_penalty.keys())

    if not subdomain_names:
        return

    scores = [max(100 - subdomain_penalty.get(name, 0), 0) for name in subdomain_names]
    domain_score = int(sum(scores) / len(scores))

    summary.domain_score = domain_score
    summary.severity = get_cvss_severity(domain_score)["severity"]


def apply_fix_result(scan_id: str, domain: str, fix_type: str, result, db: Session) -> dict:
    """
    Process a fix result from the scanner.

    Returns a dict: {success: bool, domain_score: int|None, severity: str|None}
    """
    fail = {"success": False, "domain_score": None, "severity": None}

    if not is_fix_successful(result):
        return fail

    issue_key = FIX_TYPE_TO_ISSUE_KEY.get(fix_type)
    category  = FIX_TYPE_TO_CATEGORY.get(fix_type)
    if not issue_key or not category:
        return fail

    summary = db.query(ScanSummary).filter(ScanSummary.scan_id == scan_id).first()
    if not summary:
        return fail

    removed = remove_fixed_issue(summary, issue_key, domain, category)
    if not removed:
        return fail

    scan_result = db.query(ScanResult).filter(ScanResult.scan_id == scan_id).first()
    if scan_result:
        recalculate_score(summary, scan_result)

    db.add(summary)
    db.commit()

    return {
        "success": True,
        "domain_score": summary.domain_score,
        "severity": summary.severity,
    }
