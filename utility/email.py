from datetime import UTC, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from core.config import settings


async def send_email(to_email: str, subject: str, html_body: str) -> bool:

    msg= MIMEMultipart("alternative")
    
    msg['Subject']= subject
    msg['From']= settings.EMAILS_FROM 
    msg['To']= to_email 
    msg.attach(MIMEText(html_body, "html"))
    
    await aiosmtplib.send(
        msg, hostname= settings.SMTP_HOST,
        port= settings.SMTP_PORT, start_tls= True,
        username= settings.SMTP_USER, password= settings.SMTP_PASSWORD.get_secret_value()
    )
    return True


async def send_email_verify_token(email: str, token: str) -> bool:
    
    html= f"""
    <h2>Email Verification</h2>
    <p>Click the link to verify your email
    <strong>
    <a href="{settings.BASE_URL}/api/v1/auth/verify-email?token={token}">CLICK HERE</a>
    </strong> 
    <p>This link expires in 1 hour. </p>
    <p> Ignore if you did not request for this mail.</p>
    """
    return await send_email(email, "Email Verification", html)

    
async def send_password_reset_code(email: str, otp: str) -> bool:
    html = f"""
    <h2>Password Reset</h2>
    <p>Your OTP code is: <strong>{otp}</strong></p>
    <p>This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.</p>
    """
    return await send_email(email, "Reset Your Password", html)



async def send_login_notification(email: str, username: str) -> bool:
    html = f"""
    <h2>Dear {username}</h2>
    <p>Please be informed that your account was accessed on {datetime.now(UTC).replace(microsecond=0)}</p> </br>
    <p>If you did not log into your account at the time above,
    we advice you reset your password to keep your account safe</p>
    """
    return await send_email(email, "Login Notification", html)



async def send_post_need_approval(email: str, username, post_title):
    html= f"""
    <h2>Hello Admin</h2>
    <p>Post from <strong>{username}</strong> with Title: <strong>{post_title}</strong> on {datetime.now(UTC).replace(microsecond=0)}</br>
    needs aproval to be published.
    </p>
    """
    return await send_email(email, "Post Aproval", html)


async def send_comment_notification(author_email: str, post_title: str):
    html= f"""
    <p> You have a comment notification from your "{post_title}" post </p>
    """
    return await send_email(author_email, "Comments Notification", html)