# Quick Start Guide 🚀

Get your Norwegian Cruise rewards monitor up and running in 5 minutes!

## ⚡ Super Quick Setup

### 1️⃣ Create Telegram Bot (2 minutes)

Open Telegram → Search `@BotFather` → Send these messages:

```
/newbot
My Rewards Bot
myrewardsbot_123
```

✅ Save the token BotFather gives you!

### 2️⃣ Get Your Chat ID (30 seconds)

Search `@userinfobot` on Telegram → Start chat → Copy your ID

### 3️⃣ Set Up GitHub (2 minutes)

1. **Fork this repo** (click "Fork" button above)
2. Go to your fork → **Settings** → **Secrets and variables** → **Actions**
3. Add two secrets:
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `TELEGRAM_CHAT_ID` = your chat ID
4. Go to **Actions** tab → Enable workflows
5. Click **Run workflow** to test immediately!

### 4️⃣ Start Your Bot (10 seconds)

Open Telegram → Find your bot → Send `/start`

Then try: `/check` to see current rewards!

## ✅ Done!

You'll get a notification showing the current rewards.

Then:
- **Every hour** - Automatic monitoring for changes
- **Every 5 minutes** - Bot checks for your commands
- **Anytime** - Send `/check` to get current status

When changes happen, you'll automatically get notified:
- 🎁 New rewards appear
- 📦 Rewards are removed  
- 💰 Prices change

## 🔍 Where to Check It's Working

**GitHub Actions** → Click the latest run → See the green checkmark ✅

**Telegram** → You should have received a "Monitoring started" message

**Test it live** → Send `/check` to your bot and get instant status!

## 💬 Bot Commands

Message your bot anytime:

- `/check` - Get current rewards status
- `/status` - Same as /check  
- `/help` - Show available commands

The bot responds within 5 minutes!

## ⚙️ Customize

Want it to check **every 30 minutes**?

Edit `.github/workflows/monitor.yml`:

```yaml
cron: '*/30 * * * *'  # Every 30 mins
```

Want to monitor a **different partner**?

Edit `norwegian_monitor.py`:

```python
PARTNER_URL = "https://myvip.co/rewardstore/partner/XX"
```

## 🆘 Not Working?

1. Check **Actions** tab for error logs
2. Make sure you sent `/start` to your bot
3. Verify secrets are set correctly
4. Try running workflow manually to test

## 💡 Pro Tips

- The state is saved to `rewards_state.json` - you can view it to see what's being tracked
- Check the Actions logs to see exactly what the script is finding
- You can run the workflow manually anytime to force a check
- It's completely free - uses GitHub's free tier!

---

Full documentation in [README.md](README.md)
