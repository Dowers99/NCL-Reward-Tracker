#!/usr/bin/env python3
"""
MyVIP Norwegian Cruise Rewards Monitor
Checks partner 66 for Norwegian Cruise Line rewards and notifies via Telegram
"""

import requests
import json
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import hashlib
from playwright.sync_api import sync_playwright

# Configuration from environment variables
PARTNER_URL = "https://myvip.co/rewardstore/partner/66"
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
STATE_FILE = "rewards_state.json"


class NorwegianRewardsMonitor:
    def __init__(self):
        pass

    def fetch_page(self):
        """Fetch the partner page using a real headless browser"""
        try:
            print(f"Fetching {PARTNER_URL} with Playwright...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                )
                page = context.new_page()
                response = page.goto(PARTNER_URL, wait_until='networkidle', timeout=60000)
                print(f"Page fetched successfully (status: {response.status if response else 'unknown'})")
                html = page.content()
                browser.close()
            return html
        except Exception as e:
            print(f"❌ Error fetching page: {e}")
            return None
    
    def parse_rewards(self, html_content):
        """Parse rewards from the page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract partner name
        partner_name_elem = soup.find('h1') or soup.find('h2')
        partner_name = partner_name_elem.get_text(strip=True) if partner_name_elem else "Unknown"
        
        print(f"Partner name found: {partner_name}")
        
        # Find all reward cards - based on the screenshot, they're likely in card containers
        rewards = []
        
        # Try various selectors for reward items
        reward_containers = (
            soup.find_all('div', class_=lambda x: x and 'card' in x.lower()) or
            soup.find_all('div', class_=lambda x: x and 'reward' in x.lower()) or
            soup.find_all('article') or
            soup.find_all('div', attrs={'data-reward': True})
        )
        
        print(f"Found {len(reward_containers)} potential reward containers")
        
        for container in reward_containers:
            try:
                reward = {}
                
                # Extract title (e.g., "Comp 7 Night NCL Cruise")
                title_elem = container.find(['h3', 'h4', 'h5'], class_=lambda x: not x or 'price' not in x.lower())
                if not title_elem:
                    # Try any heading
                    title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                
                if title_elem:
                    reward['title'] = title_elem.get_text(strip=True)
                
                # Extract points cost (e.g., "250,000")
                points_elem = container.find(string=lambda text: text and any(char.isdigit() for char in text) and (',' in text or len([c for c in text if c.isdigit()]) >= 3))
                if points_elem:
                    # Clean up the points value
                    points_text = ''.join(filter(lambda x: x.isdigit() or x == ',', points_elem))
                    reward['points'] = points_text
                
                # Extract image URL
                img = container.find('img')
                if img:
                    img_src = img.get('src') or img.get('data-src')
                    if img_src:
                        # Make absolute URL if needed
                        if img_src.startswith('//'):
                            img_src = 'https:' + img_src
                        elif img_src.startswith('/'):
                            img_src = 'https://myvip.co' + img_src
                        reward['image_url'] = img_src
                
                # Extract location if available
                location_elem = container.find(string=lambda text: text and 'port' in text.lower())
                if location_elem:
                    reward['location'] = location_elem.strip()
                
                # Only add if we found at least a title
                if reward.get('title'):
                    # Create unique hash for this reward
                    reward_str = f"{reward.get('title', '')}_{reward.get('points', '')}"
                    reward['hash'] = hashlib.md5(reward_str.encode()).hexdigest()
                    rewards.append(reward)
                    print(f"  ✓ Parsed: {reward['title']} - {reward.get('points', 'N/A')} points")
            
            except Exception as e:
                print(f"  ⚠ Error parsing reward container: {e}")
                continue
        
        return {
            "partner_name": partner_name,
            "partner_id": "66",
            "rewards": rewards,
            "reward_count": len(rewards),
            "timestamp": datetime.now().isoformat(),
            "url": PARTNER_URL
        }
    
    def load_previous_state(self):
        """Load previous state from file"""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠ Could not load previous state: {e}")
        return None
    
    def save_state(self, state):
        """Save current state to file"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
            print(f"✓ State saved to {STATE_FILE}")
        except Exception as e:
            print(f"❌ Error saving state: {e}")
    
    def detect_changes(self, current, previous):
        """Detect changes between current and previous states"""
        if not previous:
            return {
                "type": "first_run",
                "message": f"🎉 Monitoring started for {current['partner_name']}!",
                "current": current
            }
        
        changes = []
        
        # Check if partner name changed
        if current['partner_name'] != previous['partner_name']:
            changes.append({
                "type": "partner_changed",
                "message": f"⚠️ Partner changed from '{previous['partner_name']}' to '{current['partner_name']}'!"
            })
        
        # Check for new rewards
        current_hashes = {r['hash'] for r in current['rewards']}
        previous_hashes = {r['hash'] for r in previous['rewards']}
        
        new_hashes = current_hashes - previous_hashes
        removed_hashes = previous_hashes - current_hashes
        
        if new_hashes:
            new_rewards = [r for r in current['rewards'] if r['hash'] in new_hashes]
            changes.append({
                "type": "new_rewards",
                "message": f"🎁 {len(new_rewards)} new reward(s) added!",
                "rewards": new_rewards
            })
        
        if removed_hashes:
            removed_rewards = [r for r in previous['rewards'] if r['hash'] in removed_hashes]
            changes.append({
                "type": "removed_rewards",
                "message": f"📦 {len(removed_rewards)} reward(s) removed",
                "rewards": removed_rewards
            })
        
        # Check for price changes (same reward, different points)
        for curr_reward in current['rewards']:
            for prev_reward in previous['rewards']:
                if (curr_reward.get('title') == prev_reward.get('title') and 
                    curr_reward.get('points') != prev_reward.get('points')):
                    changes.append({
                        "type": "price_changed",
                        "message": f"💰 Price changed for '{curr_reward['title']}'",
                        "reward": curr_reward,
                        "old_points": prev_reward.get('points'),
                        "new_points": curr_reward.get('points')
                    })
        
        if not changes:
            return {
                "type": "no_changes",
                "message": f"✅ No changes detected ({current['reward_count']} rewards still available)"
            }
        
        return {
            "type": "changes_detected",
            "message": f"🔔 Changes detected for {current['partner_name']}!",
            "changes": changes,
            "current": current
        }
    
    def send_telegram_notification(self, change_data):
        """Send notification via Telegram"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("⚠️ Telegram credentials not configured, skipping notification")
            return False
        
        try:
            message = self.format_telegram_message(change_data)
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            print(f"✓ Telegram notification sent successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error sending Telegram notification: {e}")
            return False
    
    def format_telegram_message(self, change_data):
        """Format message for Telegram"""
        message_parts = []
        
        # Header
        if change_data['type'] == 'first_run':
            message_parts.append(f"🎉 <b>Norwegian Cruise Rewards Monitor Started!</b>\n")
            current = change_data['current']
            message_parts.append(f"Partner: <b>{current['partner_name']}</b>")
            message_parts.append(f"Currently tracking <b>{current['reward_count']}</b> reward(s)\n")
            
            for reward in current['rewards']:
                message_parts.append(f"• {reward['title']}")
                if reward.get('points'):
                    message_parts.append(f"  {reward['points']} points")
            
        elif change_data['type'] == 'no_changes':
            # Only send this for first run or if explicitly enabled
            return None  # Skip notification for no changes
            
        elif change_data['type'] == 'changes_detected':
            message_parts.append(f"🔔 <b>CHANGES DETECTED</b>\n")
            
            for change in change_data['changes']:
                message_parts.append(f"\n{change['message']}")
                
                if change['type'] == 'new_rewards':
                    for reward in change['rewards']:
                        message_parts.append(f"\n<b>• {reward['title']}</b>")
                        if reward.get('points'):
                            message_parts.append(f"  💰 {reward['points']} points")
                        if reward.get('location'):
                            message_parts.append(f"  📍 {reward['location']}")
                
                elif change['type'] == 'removed_rewards':
                    for reward in change['rewards']:
                        message_parts.append(f"\n<s>• {reward['title']}</s>")
                
                elif change['type'] == 'price_changed':
                    message_parts.append(f"  <s>{change['old_points']}</s> → <b>{change['new_points']}</b> points")
        
        # Footer
        message_parts.append(f"\n\n🔗 <a href='{PARTNER_URL}'>View Rewards Store</a>")
        message_parts.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        return "\n".join(message_parts)
    
    def run(self):
        """Main monitoring function"""
        print(f"\n{'='*60}")
        print(f"MyVIP Norwegian Cruise Monitor - {datetime.now()}")
        print(f"{'='*60}\n")
        
        # Fetch current state
        html = self.fetch_page()
        if not html:
            print("❌ Failed to fetch page, exiting")
            sys.exit(1)
        
        current_state = self.parse_rewards(html)
        print(f"\nCurrent state: {current_state['reward_count']} rewards found")
        
        # Load previous state
        previous_state = self.load_previous_state()
        
        # Detect changes
        changes = self.detect_changes(current_state, previous_state)
        print(f"\nChange detection: {changes['type']}")
        
        # Send notification if there are meaningful changes
        if changes['type'] in ['first_run', 'changes_detected']:
            message = self.format_telegram_message(changes)
            if message:
                print(f"\nSending Telegram notification...")
                self.send_telegram_notification(changes)
        
        # Save current state
        self.save_state(current_state)
        
        print(f"\n{'='*60}")
        print("✓ Monitoring check complete")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    monitor = NorwegianRewardsMonitor()
    monitor.run()
