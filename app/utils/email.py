import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL")


def send_invite_email(to_email: str, invite_token: str, org_name: str, org_id: str):
    """
    Send an invitation email to a user with a link to join the organization.
    Uses native SMTP (e.g. Gmail).
    """
    invite_link = f"{FRONTEND_URL}/invite?token={invite_token}&org_id={org_id}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; padding: 40px 0; }}
            .container {{ max-width: 520px; margin: 0 auto; background: #fff; border-radius: 12px;
                          box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                       padding: 32px; text-align: center; }}
            .header h1 {{ color: #fff; margin: 0; font-size: 22px; }}
            .body {{ padding: 32px; color: #333; line-height: 1.6; }}
            .btn {{ display: inline-block; background: linear-gradient(135deg, #0f3460, #533483);
                    color: #fff !important; text-decoration: none; padding: 14px 32px;
                    border-radius: 8px; font-weight: 600; margin: 20px 0; }}
            .footer {{ padding: 20px 32px; background: #f8f9fa; color: #888; font-size: 12px;
                       text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Domain Scanner</h1>
            </div>
            <div class="body">
                <p>Hello,</p>
                <p>You've been invited to join <strong>{org_name}</strong> on Domain Scanner.</p>
                <p>Click the button below to set up your account and get started:</p>
                <p style="text-align: center;">
                    <a href="{invite_link}" class="btn">Accept Invitation</a>
                </p>
                <p style="color: #e74c3c; font-size: 13px;">
                    ⏰ This invitation expires in <strong>24 hours</strong>.
                </p>
                <p style="font-size: 13px; color: #888;">
                    If the button doesn't work, copy and paste this link into your browser:<br/>
                    <a href="{invite_link}" style="color: #0f3460; word-break: break-all;">{invite_link}</a>
                </p>
            </div>
            <div class="footer">
                &copy; Domain Scanner &mdash; Secure your digital presence.
            </div>
        </div>
    </body>
    </html>
    """

    if not SMTP_USER or not SMTP_PASSWORD:
        raise ValueError("SMTP_USER and SMTP_PASSWORD must be strictly configured in .env to dispatch emails.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"You're invited to join {org_name} on Domain Scanner"
    msg["From"] = f"Domain Scanner <{SMTP_USER}>"
    msg["To"] = to_email

    part1 = MIMEText(f"You're invited to join {org_name} on Domain Scanner. Link: {invite_link}", "plain")
    part2 = MIMEText(html_content, "html")

    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
    finally:
        server.quit()
    
    return True
