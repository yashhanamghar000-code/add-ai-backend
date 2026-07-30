"""
Inline-CSS HTML email templates. Kept as plain string-building functions
(no Jinja) since there are only two templates and no designer workflow
around them yet — if that grows, swap this for a proper template engine
without touching NotificationService (it only calls these two functions).
"""
from __future__ import annotations


def _logo_block(app_name: str, logo_url: str | None) -> str:
    if logo_url:
        return f'<img src="{logo_url}" alt="{app_name}" style="max-height:40px;" />'
    return f'<span style="font-family:Georgia,serif;font-style:italic;font-size:22px;color:#1a1a2e;">{app_name}</span>'


def welcome_email_html(customer_name: str, shop_name: str, logo_url: str | None, cta_url: str) -> str:
    """Onboarding email sent once, right after a *verified* signup."""
    return f"""\
<div style="background:#f4f4f7;padding:24px 0;font-family:Arial,Helvetica,sans-serif;">
  <table role="presentation" width="100%" style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:8px;overflow:hidden;">
    <tr>
      <td style="padding:28px 32px 8px 32px;text-align:center;">
        {_logo_block(shop_name, logo_url)}
      </td>
    </tr>
    <tr>
      <td style="padding:8px 32px 0 32px;text-align:center;">
        <div style="background:#2f7ed8;border-radius:12px;padding:28px 12px;margin-top:8px;">
          <span style="display:inline-block;background:#fff;color:#1a1a2e;font-weight:800;font-size:30px;
                       letter-spacing:1px;padding:10px 22px;border-radius:6px;
                       border:3px solid #1a1a2e;box-shadow:4px 4px 0 #1a1a2e;">
            WELCOME
          </span>
        </div>
      </td>
    </tr>
    <tr>
      <td style="padding:28px 32px 0 32px;font-size:15px;line-height:1.6;color:#333;">
        <p style="margin:0 0 12px 0;">Hi {customer_name},</p>
        <p style="margin:0 0 12px 0;">We're so excited to have you on board with {shop_name}! 🎉</p>
        <p style="margin:0 0 24px 0;">
          Be the first to know about new arrivals, special offers, and updates —
          we'll only send you things worth opening.
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:0 32px;text-align:center;">
        <a href="{cta_url}" style="display:inline-block;background:#111111;color:#ffffff;
           text-decoration:none;font-weight:600;font-size:14px;padding:14px 32px;
           border-radius:6px;">Get Started</a>
      </td>
    </tr>
    <tr>
      <td style="padding:28px 32px 0 32px;font-size:14px;line-height:1.6;color:#333;">
        <p style="margin:0;">
          Enjoy your time on {shop_name}, and don't hesitate to reach out if you have any questions!
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:24px 32px 28px 32px;">
        <hr style="border:none;border-top:1px solid #eee;margin:0 0 16px 0;" />
        <p style="margin:0;font-size:11px;color:#999;text-align:center;">
          This email was sent to you because you signed up on {shop_name}.
        </p>
      </td>
    </tr>
  </table>
</div>
"""


def login_alert_email_html(customer_name: str, app_name: str, logo_url: str | None, device_info: str, cta_url: str) -> str:
    """Security notice sent on every sign-in from a *verified* address."""
    return f"""\
<div style="background:#f4f4f7;padding:24px 0;font-family:Arial,Helvetica,sans-serif;">
  <table role="presentation" width="100%" style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:8px;overflow:hidden;">
    <tr>
      <td style="padding:24px 32px;border-bottom:1px solid #eee;">
        {_logo_block(app_name, logo_url)}
      </td>
    </tr>
    <tr>
      <td style="padding:36px 32px 0 32px;text-align:center;">
        <div style="font-size:34px;line-height:1;">🔐</div>
      </td>
    </tr>
    <tr>
      <td style="padding:16px 32px 0 32px;text-align:center;">
        <h1 style="margin:0;font-size:24px;color:#1a1a2e;">New sign-in detected</h1>
      </td>
    </tr>
    <tr>
      <td style="padding:16px 40px 0 40px;text-align:center;font-size:14px;line-height:1.6;color:#555;">
        <p style="margin:0;">
          Hi {customer_name}, we noticed a new sign-in to your {app_name} account from {device_info}.
          If this was you, no action is needed. If it wasn't, secure your account below.
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:24px 32px 8px 32px;text-align:center;">
        <a href="{cta_url}" style="display:inline-block;background:#1a1a2e;color:#ffffff;
           text-decoration:none;font-weight:600;font-size:14px;padding:14px 32px;
           border-radius:6px;">Secure my account</a>
      </td>
    </tr>
    <tr>
      <td style="padding:8px 32px 32px 32px;text-align:center;font-size:12px;color:#999;">
        Please ignore this email if this sign-in was you.
      </td>
    </tr>
    <tr>
      <td style="padding:20px 32px;background:#fafafa;text-align:center;font-size:11px;color:#999;">
        You're receiving this email because we want to keep your {app_name} account secure.
      </td>
    </tr>
  </table>
</div>
"""
