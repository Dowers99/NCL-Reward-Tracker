#!/usr/bin/env python3
"""
Telegram Command Handler for MyVIP Monitor
Listens for commands from Telegram and responds with current reward state
"""

import requests
import json
import os
import re
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import hashlib
from playwright.sync_api import sync_playwright

# Configuration from environment variables
PARTNER_URL = "https://myvip.co/rewardstore/partner/66"
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
OFFSET_FILE = "telegram_offset.txt"
STATE_FILE = "rewards_state.json"


def get_last_offset():
    """Get the last processed update offset"""
    try:
        if os.path.exists(OFFSET_FILE):
            with open(OFFSET_FILE, 'r') as f:
                return int(f.read().strip())
    except:
        pass
    return 0


def save_offset(offset):
    """Save the last processed update offset"""
    try:
        with open(OFFSET_FILE, 'w') as f:
            f.write(str(offset))
    except Exception as e:
        print(f"⚠ Error saving offset: {e}")


def get_updates(offset=0):
    """Get new messages from Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        params = {
            "offset": offset,
            "timeout": 10,
            "allowed_updates": ["message"]
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error getting updates: {e}")
        return None


def send_message(text, parse_mode="HTML"):
    """Send a message via Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False


def fetch_current_rewards():
    """Fetch current rewards from the website using a real headless browser"""
    try:
        print(f"Fetching {PARTNER_URL} with Playwright...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
            )
            page = context.new_page()
            page.goto(PARTNER_URL, wait_until='networkidle', timeout=60000)
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, 'html.parser')

        # Extract partner name
        partner_name_elem = soup.find('h1') or soup.find('h2')
        partner_name = partner_name_elem.get_text(strip=True) if partner_name_elem else "Norwegian Cruises"

        # Find rewards using the same approach as norwegian_monitor.py
        rewards = []
        title_elements = soup.select('[id^="reward-title-"]')

        for title_elem in title_elements:
            try:
                reward = {'title': title_elem.get_text(strip=True)}

                container = title_elem.parent
                for _ in range(6):
                    if container is None or container.name in ['body', 'html']:
                        break
                    if any('cardContent' in c for c in container.get('class', [])):
                        break
                    container = container.parent

                if container:
                    for text_node in container.find_all(string=True):
                        text = text_node.strip()
                        if re.match(r'^\d{1,3}(,\d{3})+$', text):
                            reward['points'] = text
                            break

                    img = container.find('img')
                    if img:
                        img_src = img.get('src') or img.get('data-src')
                        if img_src:
                            if img_src.startswith('//'):
                                img_src = 'https:' + img_src
                            elif img_src.startswith('/'):
                                img_src = 'https://myvip.co' + img_src
                            reward['image_url'] = img_src

                if reward.get('title'):
                    rewards.append(reward)
            except:
                continue
        
        return {
            "partner_name": partner_name,
            "partner_id": "66",
            "rewards": rewards,
            "reward_count": len(rewards),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ Error fetching rewards: {e}")
        return None


def load_state():
    """Load the saved state"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return None


def format_current_state_message(state):
    """Format a message showing current rewards state"""
    if not state:
        return "❌ No reward data available. The monitor may not have run yet."
    
    parts = []
    parts.append(f"📊 <b>Current Rewards Status</b>\n")
    parts.append(f"Partner: <b>{state.get('partner_name', 'Unknown')}</b>")
    parts.append(f"Total rewards: <b>{state.get('reward_count', 0)}</b>")
    
    if state.get('timestamp'):
        try:
            ts = datetime.fromisoformat(state['timestamp'])
            parts.append(f"Last updated: {ts.strftime('%Y-%m-%d %H:%M UTC')}\n")
        except:
            pass
    
    rewards = state.get('rewards', [])
    if rewards:
        parts.append("\n<b>Available Rewards:</b>")
        for reward in rewards:
            parts.append(f"\n• <b>{reward.get('title', 'Unknown')}</b>")
            if reward.get('points'):
                parts.append(f"  💰 {reward['points']} points")
            if reward.get('location'):
                parts.append(f"  📍 {reward['location']}")
    else:
        parts.append("\n<i>No rewards found</i>")
    
    parts.append(f"\n\n🔗 <a href='{PARTNER_URL}'>View Rewards Store</a>")
    
    return "\n".join(parts)


def handle_command(command, message_id):
    """Handle a command from the user"""
    command = command.lower().strip()
    
    print(f"Handling command: {command}")
    
    if command == '/start':
        msg = (
            "👋 <b>MyVIP Rewards Monitor Bot</b>\n\n"
            "I'm monitoring Norwegian Cruise Line rewards (Partner 66) and will notify you of any changes.\n\n"
            "<b>Available commands:</b>\n"
            "• /check - Get current rewards status\n"
            "• /help - Show this help message\n"
            "• /status - Same as /check\n\n"
            "I automatically check for changes every hour!"
        )
        send_message(msg)
        return True
    
    elif command == '/help':
        msg = (
            "📖 <b>Help</b>\n\n"
            "<b>Commands:</b>\n"
            "• /check - Fetch and display current rewards\n"
            "• /status - Same as /check\n"
            "• /help - Show this message\n\n"
            "💡 <b>Automatic Monitoring:</b>\n"
            "I check for changes every hour automatically. "
            "When new rewards appear, prices change, or rewards are removed, "
            "I'll send you a notification immediately.\n\n"
            f"🔗 <a href='{PARTNER_URL}'>Visit Rewards Store</a>"
        )
        send_message(msg)
        return True
    
    elif command in ['/check', '/status']:
        # First, try to get fresh data from the website
        send_message("🔄 Fetching current rewards...")
        
        fresh_state = fetch_current_rewards()
        
        if fresh_state:
            # Send fresh data
            msg = format_current_state_message(fresh_state)
            send_message(msg)
        else:
            # Fall back to saved state if fetch failed
            saved_state = load_state()
            if saved_state:
                msg = format_current_state_message(saved_state)
                msg += "\n\n⚠️ <i>Note: Showing cached data (live fetch failed)</i>"
                send_message(msg)
            else:
                send_message("❌ Unable to fetch rewards. Please try again later.")
        
        return True
    
    else:
        # Unknown command
        msg = (
            f"❓ Unknown command: <code>{command}</code>\n\n"
            "Try /help to see available commands."
        )
        send_message(msg)
        return True


def process_updates():
    """Process new Telegram messages"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials not configured")
        return
    
    print(f"\n{'='*60}")
    print(f"Telegram Command Handler - {datetime.now()}")
    print(f"{'='*60}\n")
    
    last_offset = get_last_offset()
    print(f"Last processed offset: {last_offset}")
    
    # Get new updates
    result = get_updates(last_offset)
    
    if not result or not result.get('ok'):
        print("❌ Failed to get updates")
        return
    
    updates = result.get('result', [])
    print(f"Received {len(updates)} update(s)")
    
    if not updates:
        print("No new messages")
        return
    
    # Process each update
    for update in updates:
        update_id = update.get('update_id')
        message = update.get('message', {})
        
        # Only process messages from our authorized chat
        chat_id = str(message.get('chat', {}).get('id', ''))
        if chat_id != TELEGRAM_CHAT_ID:
            print(f"⚠️ Ignoring message from unauthorized chat: {chat_id}")
            save_offset(update_id + 1)
            continue
        
        # Extract command
        text = message.get('text', '').strip()
        message_id = message.get('message_id')
        
        if text.startswith('/'):
            print(f"Processing command: {text}")
            handle_command(text, message_id)
        else:
            print(f"Ignoring non-command message: {text[:50]}")
        
        # Save this offset so we don't process it again
        save_offset(update_id + 1)
    
    print(f"\n{'='*60}")
    print("✓ Command processing complete")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    process_updates()
