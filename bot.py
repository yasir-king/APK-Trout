def fetch_latest_posts():
    """Website se latest 5 published posts uthana"""
    url = f"{WP_BASE_URL}/posts?per_page=5"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=20)
        print(f"API Response Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Found {len(data)} posts from API.")
            return data
        else:
            print(f"Failed to fetch posts: {res.status_code} - {res.text[:200]}")
    except Exception as e:
        print(f"Network error: {e}")
    return []
