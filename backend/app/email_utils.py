"""
Email sending utility using Gmail SMTP.
Reads credentials from the .env file - never hardcode them here.
"""

import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def send_reset_code_email(to_email, code):
    subject = "Your Task Scheduler Password Reset Code"
    body = "Your password reset code is: " + code + "\n\nThis code expires in 15 minutes. If you did not request this, you can safely ignore this email."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())