from flask_mail import Mail, Message
from flask import current_app, render_template_string
from threading import Thread

mail = Mail()

def send_async_email(app, msg):
    """Send email asynchronously to avoid blocking the main thread"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")

def send_invite_email(user, org_name, password):
    """
    Send invitation email to a new user.
    """
    subject = f"Welcome to {org_name} - Security Training"
    sender = current_app.config['MAIL_DEFAULT_SENDER']
    
    # Simple HTML Body
    html_body = f"""
    <h2>Welcome to {org_name}!</h2>
    <p>You have been enrolled in our Security Awareness Training program.</p>
    <p>Please log in using the credentials below:</p>
    <ul>
        <li><strong>Username:</strong> {user.username}</li>
        <li><strong>Password:</strong> {password} (Please change on first login)</li>
    </ul>
    <p><a href="http://127.0.0.1:5000/login">Click here to Login</a></p>
    <br>
    <p>Stay Safe,<br>Security Team</p>
    """
    
    msg = Message(subject, sender=sender, recipients=[user.email])
    msg.html = html_body
    
    # Send in background thread
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
    print(f"Queued invite email for {user.email}")

def send_campaign_email(target_email, campaign_name, phishing_link):
    """
    Send a simulated phishing email for a campaign.
    """
    subject = "URGENT: Account Action Required"
    sender = "Security Alert <alert@secure-cloud-portal.com>" # Spoofed sender name
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #d9534f;">Security Alert</h2>
        <p>We detected unusual activity on your account.</p>
        <p>Please verify your identity immediately to avoid account suspension.</p>
        <p style="text-align: center;">
            <a href="{phishing_link}" style="background-color: #d9534f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Now</a>
        </p>
        <p style="font-size: 0.8rem; color: #777;">Reference: {campaign_name}</p>
    </div>
    """
    
    msg = Message(subject, sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[target_email])
    msg.html = html_body
    
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
    print(f"Queued campaign email for {target_email}")
