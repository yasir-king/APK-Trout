import base64
import json
import os
import sys
import google.generativeai as genai
import requests

# 1. Credentials from GitHub Secrets
AI_KEY = os.environ.get("AI_API_KEY")
WP_USER = os.environ.get("WP_USERNAME", "admin")
WP_PASS = os.environ.get("WP_APP_PASSWORD")
WP_BASE_URL = "https://apktrout.com/wp-json/wp/v2"
STATE_FILE = "bot_state.json"

if not AI_KEY or not WP_PASS:
    print("Error: AI_API_KEY ya WP_APP_PASSWORD secret mojood nahi hai.")
    sys.exit(1)

# 2. Gemini Setup
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 3. WordPress Auth
credentials = f"{WP_USER}:{WP_PASS}"
token = base64.b64encode(credentials.encode()).decode()
headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json",
    "User-Agent": "APKTrout-Bot/1.0"
}

# 4. State Management
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r") as f:
            processed_ids = set(json.load(f))
    except Exception:
        processed_ids = set()
else:
    processed_ids = set()

def fetch_posts():
    """Recent posts mangwana"""
    url = f"{WP_BASE_URL}/posts?per_page=10&status=publish,draft"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()
    print(f"Posts fetch karne me error: {res.status_code} - {res.text}")
    return []

def generate_summary(title, content):
    """AI se short summary likhwana"""
    prompt = f"""
    Write a clear, compelling 50 to 70-word short summary for this app/game.
    
    App Title: {title}
    Details: {content[:1200]}
    
    Rules:
    - Direct and engaging overview of features.
    - No robotic introductory phrases.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"AI generation failed for '{title}': {e}")
        return None

def update_post_summary(post_id, summary_html):
    """Post ki Excerpt me Summary + Read More Button update karna"""
    url = f"{WP_BASE_URL}/posts/{post_id}"
    payload = {"excerpt": summary_html}
    res = requests.post(url, json=payload, headers=headers)
    return res.status_code == 200

def main():
    posts = fetch_posts()
    if not posts:
        print("Koi post nahi mili ya API connection error.")
        return

    changes_made = False

    for post in posts:
        post_id = post["id"]
        title = post.get("title", {}).get("rendered", "")
        content = post.get("content", {}).get("rendered", "")
        post_link = post.get("link", f"https://apktrout.com/?p={post_id}")
        existing_excerpt = post.get("excerpt", {}).get("rendered", "").strip()

        # Check: Nayi post jiski summary pehle se mojood na ho
        if post_id not in processed_ids and not existing_excerpt:
            print(f"Generating summary for Post ID: {post_id} ({title})...")
            summary_text = generate_summary(title, content)
            
            if summary_text:
                # Summary + Read More link format
                summary_html = f"""<p>{summary_text}</p>
<p><a href="{post_link}" class="read-more-btn" style="display:inline-block; margin-top:8px; font-weight:bold; color:#0073aa; text-decoration:none;">Read More &raquo;</a></p>"""
                
                if update_post_summary(post_id, summary_html):
                    print(f"Success: Post {post_id} updated with summary and Read More button.")
                    processed_ids.add(post_id)
                    changes_made = True
                else:
                    print(f"Failed to update WordPress for ID: {post_id}")
        else:
            processed_ids.add(post_id)

    # State update
    with open(STATE_FILE, "w") as f:
        json.dump(list(processed_ids), f, indent=2)

    if changes_made:
        print("Done: All new posts have been updated.")
    else:
        print("Done: No new posts required an update.")

if __name__ == "__main__":
    main()
