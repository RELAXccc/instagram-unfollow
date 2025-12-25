import os
import time
import random
import json
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv()

# Configuration
USERNAME = os.environ.get("IG_USERNAME")
PASSWORD = os.environ.get("IG_PASSWORD")
SESSION_FILE = "session.json"

def human_delay(min_seconds=5, max_seconds=15):
    """Wait for a random amount of time to mimic human behavior."""
    sleep_time = random.uniform(min_seconds, max_seconds)
    print(f"--- Waiting for {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)

def get_client():
    """Logs in and saves/loads session to avoid frequent login flags."""
    cl = Client()
    # Set global delays for every request
    cl.delay_range = [2, 5] 
    
    if os.path.exists(SESSION_FILE):
        print("Loading session from cache...")
        cl.load_settings(SESSION_FILE)
    
    try:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print("Login successful.")
    except Exception as e:
        print(f"Login failed: {e}")
        return None
    return cl

def get_list_from_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            return f.read().splitlines()
    return None

if __name__ == '__main__':
    client = get_client()
    if not client:
        exit()

    user_id = client.user_id

    # 1. Fetch Followers and Following (Using your existing logic or cached files)
    # ... [Same logic as your original script to generate not_following_back.txt] ...

    # 2. Process Unfollows with Human-like Behavior
    with open("not_following_back.txt", "r") as file:
        unfollow_list = [line.strip() for line in file if line.strip()]

    print(f"Starting unfollow process for {len(unfollow_list)} users.")
    
    count = 0
    for user in unfollow_list:
        try:
            # Random long break every 10 unfollows
            if count > 0 and count % 10 == 0:
                print("Taking a long coffee break (2-5 minutes)...")
                human_delay(120, 300)

            print(f"[{count+1}] Attempting to unfollow: {user}")
            
            # Resolve username to ID first
            target_id = client.user_id_from_username(user)
            client.user_unfollow(target_id)
            
            print(f"Successfully unfollowed {user}")
            count += 1
            
            # Standard delay between actions
            human_delay(15, 45) 

        except Exception as e:
            print(f"Failed to unfollow {user}. Instagram might be rate-limiting you: {e}")
            print("Stopping script to prevent account ban.")
            break

    client.logout()
