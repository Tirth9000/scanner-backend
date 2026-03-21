from collections import defaultdict
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models import ScanSummary, ScanResult
from app.db.base import get_db

# START_SCORE = 100
# EXPECTED_PORTS = {80, 443, 993, 995, 465, 587, 8443}
# RISKY_PORTS = {8080, 8081, 8888, 3000, 5000}
# OLD_TLS = {"tls10", "tls11"}

# CATEGORY_RULES = {
#     "DNS Health": [
#         "Missing NS record",
#         "Missing TXT record",
#         "Missing MX record"
#     ],
#     "Application Security": [
#         "HTTP without HTTPS",
#         "Missing CSP header",
#         "Missing HSTS header",
#         "Missing X-Frame-Options",
#         "Missing X-Content-Type-Options"
#     ],
#     "Network Security": [
#         "Risky port exposed",
#         "Unexpected open port"
#     ],
#     "TLS Security": [
#         "443 open without TLS",
#         "Weak TLS version",
#         "Expired TLS"
#     ]
# }

# def evaluate_dns(dns):
#     penalty = 0
#     issues = []

#     if not dns:
#         return penalty, issues

#     if not dns.get("ns"):
#         penalty += 2
#         issues.append("Missing NS record")

#     if not dns.get("txt"):
#         penalty += 1
#         issues.append("Missing TXT record")

#     if not dns.get("mx"):
#         penalty += 1
#         issues.append("Missing MX record")

#     return penalty, issues


# def evaluate_http(http):
#     penalty = 0
#     issues = []

#     if not http:
#         return penalty, issues

#     scheme = http.get("scheme")
#     tls = http.get("tls", {})

#     if scheme == "http" and not tls.get("enabled"):
#         penalty += 20
#         issues.append("HTTP without HTTPS")

#     headers = http.get("headers", {})

#     if not headers.get("content_security_policy"):
#         penalty += 3
#         issues.append("Missing CSP header")

#     if not headers.get("strict_transport_security"):
#         penalty += 4
#         issues.append("Missing HSTS header")

#     if not headers.get("x_frame_options"):
#         penalty += 2
#         issues.append("Missing X-Frame-Options")

#     if not headers.get("x_content_type_options"):
#         penalty += 2
#         issues.append("Missing X-Content-Type-Options")

#     return penalty, issues


# def evaluate_port(port):
#     penalty = 0
#     issues = []

#     p = port.get("port")

#     if not p:
#         return penalty, issues

#     if p in RISKY_PORTS:
#         penalty += 10
#         issues.append(f"Risky port exposed {p}")

#     elif p not in EXPECTED_PORTS:
#         penalty += 8
#         issues.append(f"Unexpected open port {p}")

#     return penalty, issues


# def evaluate_tls(port):
#     penalty = 0
#     issues = []

#     tls = port.get("tls")

#     if not tls:
#         if port.get("port") == 443:
#             penalty += 20
#             issues.append("443 open without TLS")
#         return penalty, issues

#     version = (tls.get("version") or "").lower()

#     if tls.get("expired"):
#         penalty += 20
#         issues.append("Expired TLS")

#     if version in OLD_TLS:
#         penalty += 15
#         issues.append(f"Weak TLS version {version}")

#     return penalty, issues

# def score_subdomain(asset):

#     score = START_SCORE
#     issues = []

#     dns = asset.get("dns_collection")
#     http = asset.get("http_collection")
#     ports = asset.get("port_collection", [])

#     dns_pen, dns_issues = evaluate_dns(dns)
#     score -= dns_pen
#     issues.extend(dns_issues)

#     http_pen, http_issues = evaluate_http(http)
#     score -= http_pen
#     issues.extend(http_issues)

#     for port in ports:
#         p_pen, p_issues = evaluate_port(port)
#         score -= p_pen
#         issues.extend(p_issues)

#         tls_pen, tls_issues = evaluate_tls(port)
#         score -= tls_pen
#         issues.extend(tls_issues)

#     score = max(score, 0)

#     return {
#         "subdomain": asset.get("subdomain", "unknown"),
#         "score": score,
#         "issues": issues
#     }


# def score_domain(data):

#     results = []
#     scores = []

#     for asset in data:
#         r = score_subdomain(asset)
#         results.append(r)
#         scores.append(r["score"])

#     domain_score = int(sum(scores) / len(scores)) if scores else 0

#     return {
#         "domain_score": domain_score,
#         "subdomains": results
#     }

# def categorize_issues(results):

#     categorized = defaultdict(lambda: defaultdict(set))

#     for sub in results["subdomains"]:
#         subdomain = sub["subdomain"]

#         for issue in sub["issues"]:
#             for category, patterns in CATEGORY_RULES.items():
#                 for pattern in patterns:
#                     if issue.startswith(pattern):
#                         categorized[category][pattern].add(subdomain)

#     return {
#         cat: {issue: list(subs) for issue, subs in issues.items()}
#         for cat, issues in categorized.items()
#     }


# def generate_score(data):
#     scoring = score_domain(data)
#     categorized = categorize_issues(scoring)
#     return {
#         "domain_score": scoring["domain_score"],
#         "categorized_vulnerabilities": categorized
#     }


# def calculate_score(scan_id: str, db: Session):
#     scan = db.query(ScanResult).filter(ScanResult.scan_id == scan_id).first()
#     if not scan:
#         raise HTTPException(status_code=404, detail="Scan not found")
#     result = generate_score(scan.results["data"])

#     new_score = ScanSummary(
#         scan_id=scan_id,
#         domain_score=result["domain_score"],
#         categorized_vulnerabilities=result["categorized_vulnerabilities"]
#     )
#     db.add(new_score)
#     db.commit()
#     return new_score

START_SCORE = 100

SAFE_PORTS = {80, 443, 993, 995, 465, 587}
EXPECTED_PORTS = {80, 443, 993, 995, 465, 587, 8443}
RISKY_PORTS = {8080, 8081, 8888, 3000, 5000}

OLD_TLS = {"tls10", "tls11"}

CATEGORY_RULES = {
    "DNS Security": [
        "Missing NS record",
        "Missing TXT record",
        "Missing MX record"
    ],
    "Application Security": [
        "HTTP without HTTPS",
        "Missing CSP header",
        "Missing HSTS header",
        "Missing X-Frame-Options",
        "Missing X-Content-Type-Options"
    ],
    "Network Security": [
        "Risky port exposed",
        "Unexpected open port"
    ],
    "TLS Security": [
        "443 open without TLS",
        "Weak TLS version",
        "Expired TLS"
    ]
}


def evaluate_dns(dns):
    penalty = 0
    issues = []

    if not dns:
        return penalty, issues

    if not dns.get("ns"):
        penalty += 2
        issues.append("Missing NS record")

    if not dns.get("txt"):
        penalty += 1
        issues.append("Missing TXT record")

    if not dns.get("mx"):
        penalty += 1
        issues.append("Missing MX record")

    return penalty, issues


def evaluate_http(http):
    penalty = 0
    issues = []

    if not http:
        return penalty, issues

    scheme = http.get("scheme")
    tls = http.get("tls", {})

    if scheme == "http" and not tls.get("enabled"):
        penalty += 20
        issues.append("HTTP without HTTPS")

    headers = http.get("headers", {})

    if not headers.get("content_security_policy"):
        penalty += 3
        issues.append("Missing CSP header")

    if not headers.get("strict_transport_security"):
        penalty += 4
        issues.append("Missing HSTS header")

    if not headers.get("x_frame_options"):
        penalty += 2
        issues.append("Missing X-Frame-Options")

    if not headers.get("x_content_type_options"):
        penalty += 2
        issues.append("Missing X-Content-Type-Options")

    return penalty, issues


def evaluate_port(port):
    penalty = 0
    issues = []

    p = port.get("port")

    if not p:
        return penalty, issues

    if p in RISKY_PORTS:
        penalty += 10
        issues.append(f"Risky port exposed {p}")

    elif p not in EXPECTED_PORTS:
        penalty += 8
        issues.append(f"Unexpected open port {p}")

    return penalty, issues


def evaluate_tls(port):
    penalty = 0
    issues = []

    tls = port.get("tls")

    if not tls:
        if port.get("port") == 443:
            penalty += 20
            issues.append("443 open without TLS")
        return penalty, issues

    version = (tls.get("version") or "").lower()

    if tls.get("expired"):
        penalty += 20
        issues.append("Expired TLS")

    if version in OLD_TLS:
        penalty += 15
        issues.append(f"Weak TLS version {version}")

    return penalty, issues


def get_cvss_severity(score):

    # convert 0-100 → 0-10 scale
    cvss_score = round((100 - score) / 10, 1)

    if cvss_score >= 9.0:
        severity = "Critical"
    elif cvss_score >= 7.0:
        severity = "High"
    elif cvss_score >= 4.0:
        severity = "Medium"
    else:
        severity = "Low"

    return {
        "cvss_score": cvss_score,
        "severity": severity
    }

def score_subdomain(asset):
    score = START_SCORE
    issues = []
    category_penalties = defaultdict(int)

    dns = asset.get("dns_collection")
    http = asset.get("http_collection")
    ports = asset.get("port_collection", [])

    dns_pen, dns_issues = evaluate_dns(dns)
    score -= dns_pen
    issues.extend(dns_issues)
    category_penalties["DNS Health"] += dns_pen

    http_pen, http_issues = evaluate_http(http)
    score -= http_pen
    issues.extend(http_issues)
    category_penalties["Application Security"] += http_pen

    for port in ports:
        p_pen, p_issues = evaluate_port(port)
        score -= p_pen
        issues.extend(p_issues)
        category_penalties["Network Security"] += p_pen

        tls_pen, tls_issues = evaluate_tls(port)
        score -= tls_pen
        issues.extend(tls_issues)
        category_penalties["TLS Security"] += tls_pen

    score = max(score, 0)

    return {
        "subdomain": asset.get("subdomain", "unknown"),
        "score": score,
        "issues": issues,
        "category_penalties": dict(category_penalties)
    }


def score_domain(data):
    results = []
    scores = []

    for asset in data:
        r = score_subdomain(asset)
        results.append(r)
        scores.append(r["score"])

    domain_score = int(sum(scores) / len(scores)) if scores else 0

    cvss = get_cvss_severity(domain_score)

    return {
        "domain_score": domain_score,
        "cvss_score": cvss["cvss_score"],
        "severity": cvss["severity"],
        "subdomains": results
    }


def categorize_issues(results, raw_data):
    categorized = defaultdict(lambda: defaultdict(list))
    asset_map = {a.get("subdomain"): a for a in raw_data}
    for sub in results["subdomains"]:
        subdomain = sub["subdomain"]
        asset = asset_map.get(subdomain, {})
        ip = None
        dns = asset.get("dns_collection", {})
        if dns and dns.get("a"):
            ip = dns.get("a")[0]

        ports = [p.get("port") for p in asset.get("port_collection", []) if p.get("port")]

        for issue in sub["issues"]:

            for category, patterns in CATEGORY_RULES.items():

                for pattern in patterns:

                    if issue.startswith(pattern):

                        # Base entry (default)
                        severity_data = get_cvss_severity(sub["score"])

                        entry = {
                            "subdomain": subdomain,
                            "ip": ip,
                            "severity": severity_data["severity"]
                        }
                        # Only add port for Network Security
                        if category == "Network Security":

                            issue_port = None
                            for p in ports:
                                if str(p) in issue:
                                    issue_port = p
                                    break

                            entry["port"] = issue_port

                        # Avoid duplicates
                        if entry not in categorized[category][pattern]:
                            categorized[category][pattern].append(entry)
    return categorized

def calculate_score(scan_id: str, db: Session):
    scan = db.query(ScanResult).filter(
        ScanResult.scan_id == scan_id
    ).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    data = scan.results
    scoring = score_domain(data['data'])
    categorized = categorize_issues(scoring, data['data'])
    ips_of_scan = get_ips_from_scan(data)
    new_score = ScanSummary(
        scan_id=scan_id,
        domain_score=scoring["domain_score"],
        severity=scoring["severity"],
        cvss_score=scoring["cvss_score"],
        categorized_vulnerabilities=categorized
        )
    db.add(new_score)

    db.commit()
    return {
        "scan_id": scan_id,
        "domain_score": scoring["domain_score"],
        "severity": scoring["severity"],
        "categorized_vulnerabilities": categorized,
        "ips": ips_of_scan
    }

def get_ips_from_scan(data: dict):
    ips = []

    for item in data.get("data", []):
        http_data = item.get("http_collection")

        if http_data and http_data.get("ip"):
            ips.append(http_data["ip"])
        ips = list(set(ips))
    return ips