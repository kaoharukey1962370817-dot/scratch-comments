import requests
import json
import time

STUDIO_ID = "YOUR_STUDIO_ID"

all_comments = []

offset = 0
limit = 40

def fetch_replies(comment_id):
    url = f"https://api.scratch.mit.edu/studios/{STUDIO_ID}/comments/{comment_id}/replies"
    res = requests.get(url)

    if res.status_code != 200:
        return []

    return res.json()

while True:
    url = f"https://api.scratch.mit.edu/studios/{STUDIO_ID}/comments?limit={limit}&offset={offset}"
    
    print(f"取得中 offset={offset}")
    
    res = requests.get(url)

    if res.status_code != 200:
        print("エラー:", res.status_code)
        break

    comments = res.json()

    if not comments:
        print("全件取得完了")
        break

    for c in comments:
        # 親コメント
        all_comments.append({
            "id": c["id"],
            "content": c["content"],
            "datetime_created": c["datetime_created"],
            "author": c["author"],
            "parent_id": None
        })

        # 🔥 返信を別APIで取得
        replies = fetch_replies(c["id"])

        for r in replies:
            all_comments.append({
                "id": r["id"],
                "content": r["content"],
                "datetime_created": r["datetime_created"],
                "author": r["author"],
                "parent_id": c["id"]
            })

        time.sleep(0.2)

    offset += limit
    time.sleep(0.5)

# 時間順
all_comments.sort(key=lambda x: x["datetime_created"])

with open("comments.json", "w", encoding="utf-8") as f:
    json.dump(all_comments, f, ensure_ascii=False, indent=2)

print(f"保存完了: {len(all_comments)}件")
