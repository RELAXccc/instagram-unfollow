import os
import time
import random
import json
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
USERNAME = os.environ.get("IG_USERNAME")
PASSWORD = os.environ.get("IG_PASSWORD")
VERIFICATION_CODE = os.environ.get("IG_2FA")
SESSION_FILE = "session.json"
MAX_UNFOLLOWS_PER_SESSION = 40  # Safety limit for 2025

def human_delay(min_sec=15, max_sec=45):
    """Wait for a random amount of time to mimic human behavior."""
    sleep_time = random.uniform(min_sec, max_sec)
    print(f"--- Sleeping for {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)

def check_if_cached_exists(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            return f.read().splitlines()
    return None

def get_followers(client, user_id):
    if (follower_list := check_if_cached_exists("followers.txt")) is not None:
        print("Using cached followers list.")
        return follower_list
    
    print("Fetching followers from Instagram...")
    followers = client.user_followers(user_id)
    follower_list = [f.username for ig_id, f in followers.items() if hasattr(f, 'username')]
    
    with open("followers.txt", "w") as f:
        f.write("\n".join(follower_list))
    return follower_list

def get_following(client, user_id):
    if (following_list := check_if_cached_exists("following.txt")) is not None:
        print("Using cached following list.")
        return following_list
    
    print("Fetching following list from Instagram...")
    following = client.user_following(user_id)
    following_list = [f.username for ig_id, f in following.items() if hasattr(f, 'username')]
    
    with open("following.txt", "w") as f:
        f.write("\n".join(following_list))
    return following_list

if __name__ == '__main__':
    client = Client()
    client.delay_range = [2, 5]

    # Session Management
    if os.path.exists(SESSION_FILE):
        print("Loading session from cache...")
        client.load_settings(SESSION_FILE)

    try:
        print(f"Logging in as {USERNAME}...")
        client.login(USERNAME, PASSWORD, verification_code=VERIFICATION_CODE)
        client.dump_settings(SESSION_FILE)
    except Exception as e:
        print(f"Login failed: {e}")
        exit()

    user_id = str(client.user_id)

    # 1. Compare Followers vs Following
    follower_usernames = get_followers(client, user_id)
    following_usernames = get_following(client, user_id)
    
    not_following_back = [u for u in following_usernames if u not in follower_usernames]

    with open("not_following_back.txt", "w") as file:
        file.write("\n".join(not_following_back))

    # 2. Curation Step
    print(f"\nFound {len(not_following_back)} users who don't follow you back.")
    input("Check 'not_following_back.txt', remove people to keep, SAVE, and press Enter here...")

    # 3. Unfollow Loop
    with open("not_following_back.txt", "r") as file:
        curated_list = [line.strip() for line in file if line.strip()]

    count = 0
    for user in curated_list:
        if count >= MAX_UNFOLLOWS_PER_SESSION:
            print(f"Safety limit of {MAX_UNFOLLOWS_PER_SESSION} reached. Stopping.")
            break

        try:
            # Periodic long break
            if count > 0 and count % 8 == 0:
                print("Taking a 3-minute break to stay under the radar...")
                time.sleep(180)

            print(f"[{count+1}/{len(curated_list)}] Unfollowing: {user}")
            
            # The 'TypeError' usually happens here; we catch it but continue
            target_id = client.user_id_from_username(user)
            client.user_unfollow(target_id)
            
            print(f"Success: {user} unfollowed.")
            count += 1
            human_delay()

        except Exception as e:
            print(f"Error processing {user}: {e}")
            print("Likely a rate limit. Stopping to protect account.")
            break

    client.logout()
    print("Process complete.")
