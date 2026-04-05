import requests
import json
import time
import os
from datetime import datetime

STUDIO_ID = "51471940"

LIMIT = 40
MAX_PER_RUN = 2000

PROGRESS_FILE = "progress.txt"
OUTPUT_FILE = "comments.json"

# -----------------------
# progress強制生成（超重要）
# -----------------------
if not os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "w") as f:
        f.write("0")

# -----------------------
# 進行状況読み込み
# -----------------------
with open(PROGRESS_FILE, "r") as f:
    offset = int(f.read().strip())

print(f"▶ 開始 offset={offset}")

# -----------------------
# 既存データ
# -----------------------
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        all_comments = json.load(f)
else:
    all_comments = []

existing_ids = set(c["id"] for c in all_comments)

# -----------------------
# 時間変換
# -----------------------
def convert_time(dt):
    return int(datetime.fromisoformat(dt.replace("Z", "+00:00")).timestamp())

# -----------------------
# 返信取得
# -----------------------
def fetch_replies(comment_id):
    url = f"https://api.scratch.mit.edu/studios/{STUDIO_ID}/comments/{comment_id}/replies"
    res = requests.get(url)

    if res.status_code != 200:
        return []

    return res.json()

# -----------------------
# メイン
# -----------------------
start_offset = offset

while offset < start_offset + MAX_PER_RUN:

    url = f"https://api.scratch.mit.edu/studios/{STUDIO_ID}/comments?limit={LIMIT}&offset={offset}"
    print(f"取得中 offset={offset}")

    res = requests.get(url)

    if res.status_code != 200:
        print("❌ エラー:", res.status_code)
        break

    comments = res.json()

    if not comments:
        print("🎉 全件取得完了")
        offset = 0
        break

    for c in comments:

        # 親コメント
        if c["id"] not in existing_ids:
            all_comments.append({
                "id": c["id"],
                "user": c["author"]["username"],
                "text": c["content"],
                "time": convert_time(c["datetime_created"]),
                "parent_id": None
            })
            existing_ids.add(c["id"])

        # 返信
        replies = fetch_replies(c["id"])

        for r in replies:
            if r["id"] not in existing_ids:
                all_comments.append({
                    "id": r["id"],
                    "user": r["author"]["username"],
                    "text": r["content"],
                    "time": convert_time(r["datetime_created"]),
                    "parent_id": c["id"]
                })
                existing_ids.add(r["id"])

        time.sleep(0.2)

    offset += LIMIT

    # 🔥 必ず保存
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(offset))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_comments, f, ensure_ascii=False)

# -----------------------
# ソート
# -----------------------
all_comments.sort(key=lambda x: x["time"])

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_comments, f, ensure_ascii=False, indent=2)

print(f"💾 保存完了: {len(all_comments)}件")
print(f"📍 次回 offset={offset}")
