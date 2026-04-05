import requests
import json
import time
import os

STUDIO_ID = "51471940"

LIMIT = 40
MAX_PER_RUN = 2000  # ← 1回で進める量（調整OK）

# 🔥 進行状況ファイル
PROGRESS_FILE = "progress.txt"
OUTPUT_FILE = "comments.json"

# -----------------------
# 進行状況読み込み
# -----------------------
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        offset = int(f.read().strip())
else:
    offset = 0

print(f"▶ 開始 offset={offset}")

# -----------------------
# 既存データ読み込み
# -----------------------
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        all_comments = json.load(f)
else:
    all_comments = []

# 重複防止
existing_ids = set(c["id"] for c in all_comments)

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
# メインループ
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
        offset = 0  # リセット（次回用）
        break

    for c in comments:

        # 親コメント
        if c["id"] not in existing_ids:
            all_comments.append({
                "id": c["id"],
                "content": c["content"],
                "datetime_created": c["datetime_created"],
                "author": c["author"],
                "parent_id": None
            })
            existing_ids.add(c["id"])

        # 🔥 返信取得
        replies = fetch_replies(c["id"])

        for r in replies:
            if r["id"] not in existing_ids:
                all_comments.append({
                    "id": r["id"],
                    "content": r["content"],
                    "datetime_created": r["datetime_created"],
                    "author": r["author"],
                    "parent_id": c["id"]
                })
                existing_ids.add(r["id"])

        time.sleep(0.05)

    offset += LIMIT

    # 🔥 途中保存（超重要）
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(offset))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_comments, f, ensure_ascii=False)

# -----------------------
# 最後にソート
# -----------------------
all_comments.sort(key=lambda x: x["datetime_created"])

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_comments, f, ensure_ascii=False, indent=2)

print(f"💾 保存完了: {len(all_comments)}件")
print(f"📍 次回 offset={offset}")
