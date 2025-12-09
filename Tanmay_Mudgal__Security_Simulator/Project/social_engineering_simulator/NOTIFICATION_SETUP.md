# 📱 Discord & Telegram Notification Setup Guide

This guide will help you set up Discord and Telegram notifications for meeting requests.

## 🎯 Discord Webhook Setup (2 minutes)

1. **Open Discord** and go to your server
2. **Right-click** on the channel where you want notifications
3. Click **Edit Channel** → **Integrations** → **Webhooks**
4. Click **New Webhook**
5. Give it a name (e.g., "Meeting Bot")
6. **Copy the Webhook URL**
7. Add it to your `.env` file:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE
   ```

### Example Discord Notification:
```
🎯 New Meeting Request!
Someone just clicked 'Book a Meeting' button

👤 Name: John Doe
📧 Email: john@example.com
💬 Message: Interested in security services
🌐 IP Address: 192.168.1.1
🕐 Time: 2025-12-05 23:14:37
```

---

## 📲 Telegram Bot Setup (5 minutes)

### Step 1: Create Telegram Bot
1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the prompts:
   - Choose a **name** for your bot (e.g., "Meeting Notifier")
   - Choose a **username** (must end with 'bot', e.g., "my_meeting_bot")
4. **Copy the Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID
1. Search for **@userinfobot** in Telegram
2. Start a chat with it
3. It will send you your **Chat ID** (a number)
4. **Save this Chat ID**

### Step 3: Start Your Bot
1. Search for your bot username in Telegram
2. Click **Start** to initiate the bot

### Step 4: Add to .env File
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=your_chat_id_here
```

### Example Telegram Notification:
```
🎯 New Meeting Request!

👤 Name: John Doe
📧 Email: john@example.com
💬 Message: Interested in security services

🌐 IP Address: 192.168.1.1
🕐 Time: 2025-12-05 23:14:37

From: Social Engineering Simulator
```

---

## ⚙️ Final Setup

1. Update your `.env` file with all credentials:
   ```env
   # Discord Notification
   DISCORD_WEBHOOK_URL=your_discord_webhook_url_here

   # Telegram Notification
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

2. **Restart your Flask application**

3. Test it by clicking "Book a Meeting" on the Services page!

---

## 🔧 Troubleshooting

### Discord not working?
- Make sure the webhook URL starts with `https://discord.com/api/webhooks/`
- Check that the webhook is in the correct channel
- Verify the webhook wasn't deleted

### Telegram not working?
- Make sure you've **started** the bot (sent /start message)
- Verify your Chat ID is correct (it's a number, not a username)
- Check that the bot token is correct
- Make sure the bot token and chat ID don't have extra spaces

### Neither working?
- Check if the `.env` file is in the correct location
- Restart the Flask application after adding credentials
- Check the console logs for error messages

---

## 🎉 Features

✅ Instant notifications to Discord and/or Telegram
✅ Beautiful formatted messages with emojis  
✅ Captures name, email, message, IP, and timestamp
✅ Automatic fallback (if one fails, the other still works)
✅ User-friendly modal form

---

## 📝 Notes

- You can use **just Discord**, **just Telegram**, or **both**
- If one service is not configured, the other will still work
- Notifications are sent asynchronously (won't slow down your app)
- IP addresses are logged for security purposes

Enjoy your notifications! 🚀
