import json
import os
import re
import google.generativeai as genai
import requests

# 1. API Key Setup
AI_KEY = os.environ.get("AI_API_KEY")
WP_BASE_URL = "https://apktrout.com/wp-json/wp/v2"
POSTS_DIR = "posts"
STATE_FILE = "bot_state.json"

if not AI_KEY:
    print("Error: AI_API_KEY secret mojood nahi hai.")
    exit(1)

genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 2. State file load karna
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            processed_ids = set(json.load(f))
    except Exception:
        processed_ids = set()
else:
    processed_ids = set()

def fetch_latest_posts():
    """Website se latest 5 published posts uthana"""
    url = f"{WP_BASE_URL}/posts?per_page=5&status=publish"
    try:
        res = requests.get(url, timeout=20)
        if res.status_code == 200:
            return res.json()
        print(f"Failed to fetch posts: {res.status_code}")
    except Exception as e:
        print(f"Network error: {e}")
    return []

def clean_html(raw_html):
    """HTML tags ko clean text banana"""
    clean_text = re.sub(r"<[^>]+>", "", raw_html)
    return clean_text.strip()

def generate_summary(title, content):
    """AI se 50-70 words ki short summary likhwana"""
    prompt = f"""
    Write a clear, compelling 50 to 70-word short summary for this app/game.
    Directly focus on main features and use-case. Avoid any robotic introductory fluff.

    App Title: {title}
    App Details: {content[:1200]}
    """
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        print(f"AI error for '{title}': {e}")
        return None

def main():
    posts = fetch_latest_posts()
    if not posts:
        print("Koi post nahi mili ya API access nahi ho raha.")
        return

    os.makedirs(POSTS_DIR, exist_ok=True)
    new_posts_added = False

    for post in posts:
        post_id = post["id"]

        # Agar pehle se ban chuki hai to skip karein
        if post_id in processed_ids:
            continue

        title = clean_html(post.get("title", {}).get("rendered", "Untitled App"))
        raw_content = clean_html(post.get("content", {}).get("rendered", ""))
        post_link = post.get("link", f"https://apktrout.com/?p={post_id}")

        print(f"Generating summary for: {title} (ID: {post_id})...")
        summary = generate_summary(title, raw_content)

        if summary:
            # File name ko clean slug banana
            slug = re.sub(r"[^\w\s-]", "", title).strip().lower()
            slug = re.sub(r"[-\s]+", "-", slug)[:40]
            filename = f"{POSTS_DIR}/{post_id}_{slug}.md"

            # Markdown Content format
            md_content = f"""# {title}

{summary}

---

👉 [**Read Full Article & Download on APK Trout**]({post_link})
"""
            with open(filename, "w", encoding="utf-8") as f:
                f.write(md_content)

            processed_ids.add(post_id)
            new_posts_added = True
            print(f"Public post saved: {filename}")

    # State update
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed_ids), f, indent=2)

    if new_posts_added:
        print("Done: Nayi posts ki summary files commit ke liye tayar hain.")
    else:
        print("Done: Tamam posts pehle se bani hui hain.")

if __name__ == "__main__":
    main()
