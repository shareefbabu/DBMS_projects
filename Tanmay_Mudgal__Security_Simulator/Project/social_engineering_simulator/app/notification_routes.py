from flask import Blueprint, request, jsonify, current_app
import requests
from datetime import datetime
import os

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/book-meeting', methods=['POST'])
def book_meeting():
    """Handle meeting booking and send notifications to Discord and Telegram"""
    print("=" * 50)
    print("📅 MEETING REQUEST RECEIVED")
    print("=" * 50)
    
    try:
        # Get data from request
        data = request.get_json()
        print(f"Request data: {data}")
        
        name = data.get('name', 'Unknown')
        email = data.get('email', 'Not provided')
        message = data.get('message', 'No message')
        
        # Get user info
        ip_address = request.remote_addr
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Message: {message}")
        print(f"IP: {ip_address}")
        print(f"Time: {timestamp}")
        
        # Send Discord notification
        print("\n🎯 Attempting Discord notification...")
        discord_sent = send_discord_notification(name, email, message, ip_address, timestamp)
        print(f"Discord sent: {discord_sent}")
        
        # Send Telegram notification
        print("\n📲 Attempting Telegram notification...")
        telegram_sent = send_telegram_notification(name, email, message, ip_address, timestamp)
        print(f"Telegram sent: {telegram_sent}")
        
        print("\n✅ Meeting booking completed!")
        print("=" * 50)
        
        return jsonify({
            'success': True,
            'discord_sent': discord_sent,
            'telegram_sent': telegram_sent,
            'message': 'Meeting request received! We will contact you soon.'
        }), 200
        
    except Exception as e:
        print(f"\n❌ ERROR in book_meeting: {str(e)}")
        print("=" * 50)
        current_app.logger.error(f"Error booking meeting: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500


def send_discord_notification(name, email, message, ip_address, timestamp):
    """Send notification to Discord via webhook"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    
    if not webhook_url:
        current_app.logger.warning("Discord webhook URL not configured")
        return False
    
    try:
        embed = {
            "title": "🎯 New Meeting Request!",
            "description": f"Someone just clicked 'Book a Meeting' button",
            "color": 0xf97316,  # Orange color
            "fields": [
                {"name": "👤 Name", "value": name, "inline": True},
                {"name": "📧 Email", "value": email, "inline": True},
                {"name": "💬 Message", "value": message or "No message provided", "inline": False},
                {"name": "🌐 IP Address", "value": ip_address, "inline": True},
                {"name": "🕐 Time", "value": timestamp, "inline": True}
            ],
            "footer": {
                "text": "Social Engineering Simulator"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        payload = {
            "embeds": [embed],
            "username": "Meeting Bot"
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        current_app.logger.info("Discord notification sent successfully")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send Discord notification: {str(e)}")
        return False


def send_telegram_notification(name, email, message, ip_address, timestamp):
    """Send notification to Telegram via bot"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"Bot Token: {'*' * 10 if bot_token else 'NOT SET'}")
    print(f"Chat ID: {chat_id if chat_id else 'NOT SET'}")
    
    if not bot_token or not chat_id:
        print("⚠️  Telegram credentials not configured")
        current_app.logger.warning("Telegram bot credentials not configured")
        return False
    
    try:
        # Create formatted message
        telegram_message = f"""
🎯 *New Meeting Request!*

👤 *Name:* {name}
📧 *Email:* {email}
💬 *Message:* {message or 'No message provided'}

🌐 *IP Address:* `{ip_address}`
🕐 *Time:* {timestamp}

_From: Social Engineering Simulator_
"""
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': telegram_message,
            'parse_mode': 'Markdown'
        }
        
        print(f"Sending to Telegram API: {url[:50]}...")
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"Telegram API Response Status: {response.status_code}")
        print(f"Telegram API Response: {response.text[:200]}")
        
        response.raise_for_status()
        
        print("✅ Telegram notification sent successfully!")
        current_app.logger.info("Telegram notification sent successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send Telegram notification: {str(e)}")
        current_app.logger.error(f"Failed to send Telegram notification: {str(e)}")
        return False
