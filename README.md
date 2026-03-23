# Norwegian Cruise Rewards Monitor 🚢

Automatically monitors MyVIP.co Partner 66 (Norwegian Cruise Line) for new rewards and sends Telegram notifications when changes are detected.

Runs completely free on GitHub Actions - no server costs, no need to keep your PC running!

## Features

- ✅ Monitors Norwegian Cruise Line rewards every hour
- ✅ Detects new rewards added to the store
- ✅ Detects removed rewards
- ✅ Detects price changes (points required)
- ✅ Alerts if partner name changes (e.g., if partner 66 becomes a different company)
- ✅ Sends rich notifications via Telegram
- ✅ **Interactive bot commands** - message your bot anytime to check status
- ✅ Completely free hosting on GitHub Actions
- ✅ No maintenance required after setup

## Setup Instructions

### Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat and send `/newbot`
3. Follow the prompts to name your bot (e.g., "MyVIP Rewards Monitor")
4. BotFather will give you a **Bot Token** - save this! It looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   ```

### Step 2: Get Your Telegram Chat ID

1. Search for `@userinfobot` on Telegram
2. Start a chat and it will immediately reply with your Chat ID
3. Save your **Chat ID** - it looks like: `123456789`

Alternatively, you can:
1. Message your new bot (the one you just created)
2. Visit this URL in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Look for `"chat":{"id":123456789}` in the response

### Step 3: Fork This Repository

1. Click the "Fork" button at the top right of this GitHub repository
2. This creates your own copy of the project

### Step 4: Add Secrets to Your Fork

1. Go to your forked repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: Your bot token from Step 1

4. Click **New repository secret** again and add:

   - Name: `TELEGRAM_CHAT_ID`
   - Value: Your chat ID from Step 2

### Step 5: Enable GitHub Actions

1. Go to the **Actions** tab in your forked repository
2. Click **"I understand my workflows, go ahead and enable them"**
3. The monitor will now run automatically every hour!

### Step 6: Test It (Optional)

1. Go to **Actions** tab
2. Click on "Norwegian Cruise Rewards Monitor" workflow
3. Click **Run workflow** → **Run workflow**
4. This will run the monitor immediately instead of waiting for the next hour
5. You should receive a Telegram message with the current rewards!

## How It Works

1. **Every hour**, GitHub Actions automatically runs the monitoring script
2. The script:
   - Fetches the Norwegian Cruise Line partner page
   - Extracts all reward information (titles, points, images)
   - Compares with the previous state
   - Detects any changes (new rewards, removed rewards, price changes)
   - Sends a Telegram notification if changes are found
   - Saves the current state for the next check

3. **You get notified** via Telegram whenever:
   - New rewards are added ✨
   - Rewards are removed 📦
   - Prices change 💰
   - The partner name changes ⚠️

## Interactive Bot Commands

You can message your bot anytime to check the current status! The bot checks for your messages every 5 minutes.

### Available Commands

- **`/check`** - Fetch and display current rewards right now
- **`/status`** - Same as /check
- **`/help`** - Show available commands
- **`/start`** - Welcome message and command list

### How to Use

Just open Telegram and message your bot:

```
/check
```

The bot will immediately fetch the current rewards from the website and send you a detailed status:

```
📊 Current Rewards Status

Partner: Norwegian Cruises
Total rewards: 2

Available Rewards:

• Comp 7 Night NCL Cruise
  💰 250,000 points

• Comp 3-4 Night NCL Cruise
  💰 250,000 points

🔗 View Rewards Store
```

**Why this is useful:**
- ✅ Test that the monitoring is working
- ✅ Check rewards anytime without waiting for changes
- ✅ Get instant status updates on demand
- ✅ Confirm the bot is alive and connected

## Notification Examples

### When New Rewards Are Added:
```
🔔 CHANGES DETECTED

🎁 1 new reward(s) added!

• Comp 10 Night Mediterranean Cruise
  💰 350,000 points
  📍 Various Ports

🔗 View Rewards Store
⏰ 2024-12-19 15:00:00 UTC
```

### When Prices Change:
```
🔔 CHANGES DETECTED

💰 Price changed for 'Comp 7 Night NCL Cruise'
  250,000 → 200,000 points

🔗 View Rewards Store
⏰ 2024-12-19 15:00:00 UTC
```

## Customization

### Change Check Frequency

Edit `.github/workflows/monitor.yml`:

```yaml
schedule:
  - cron: '0 * * * *'  # Every hour
  # - cron: '*/30 * * * *'  # Every 30 minutes
  # - cron: '0 */2 * * *'  # Every 2 hours
  # - cron: '0 9,17 * * *'  # At 9 AM and 5 PM UTC
```

### Monitor Different Partners

Edit `norwegian_monitor.py` and change:

```python
PARTNER_URL = "https://myvip.co/rewardstore/partner/66"
# Change to any partner ID you want to monitor
```

### Add Email Notifications

You can extend the script to also send emails. Add these secrets:
- `EMAIL_SMTP_SERVER`
- `EMAIL_SMTP_PORT`
- `EMAIL_FROM`
- `EMAIL_PASSWORD`
- `EMAIL_TO`

Then modify the `send_telegram_notification` method to also send emails.

## Troubleshooting

### Not Receiving Notifications

1. **Check GitHub Actions logs**:
   - Go to Actions tab → Click on the latest run → View logs
   
2. **Verify secrets are set correctly**:
   - Settings → Secrets and variables → Actions
   - Make sure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set

3. **Test your bot**:
   - Send a message to your bot on Telegram
   - It should respond (or at least not show an error)

4. **Make sure you started your bot**:
   - Send `/start` to your bot on Telegram

### Workflow Not Running

1. **Check if Actions are enabled**:
   - Actions tab → Make sure workflows are enabled

2. **GitHub requires activity**:
   - If the repository is inactive for 60 days, scheduled workflows stop
   - Make any small commit to re-enable them

### Want to Run Locally for Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"

# Run the monitor
python norwegian_monitor.py
```

## Files Explained

- `norwegian_monitor.py` - Main monitoring script (runs hourly)
- `telegram_handler.py` - Interactive command handler (runs every 5 minutes)
- `.github/workflows/monitor.yml` - GitHub Actions workflow for hourly monitoring
- `.github/workflows/telegram_commands.yml` - GitHub Actions workflow for command handling
- `requirements.txt` - Python dependencies
- `rewards_state.json` - Stores the last known state (auto-generated)
- `telegram_offset.txt` - Tracks processed Telegram messages (auto-generated)

## Cost

**$0** - Completely free! GitHub Actions provides 2,000 minutes/month for free.

**Usage breakdown:**
- Main monitor: 24 runs/day × 30 days × ~30 seconds = ~360 minutes/month
- Command handler: 288 runs/day × 30 days × ~10 seconds = ~1,440 minutes/month
- **Total: ~1,800 minutes/month**

You're well within the free tier!

## Privacy & Security

- Your Telegram bot token and chat ID are stored as encrypted secrets in GitHub
- The script only reads from myvip.co, it doesn't modify anything
- No personal data is stored or transmitted except to your own Telegram

## License

MIT - Do whatever you want with it!

## Questions?

Open an issue on GitHub or check the GitHub Actions logs for debugging.

Happy reward hunting! 🎁🚢
