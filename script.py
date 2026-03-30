import requests
import json
import time

studio_id = "51471940"

def fetch_comments(offset):
    url = f"https://api.scratch.mit.edu/studios/{studio_id}/comments"
    params = {"limit": 40, "offset": offset}
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, params=params, headers=headers)

    if res.status_code != 200:
        print("エラー:", res.status_code)
        return []
    return res.json()

all_comments = []
offset = 0

print("🚀 一発取得開始")

while True:
    data = fetch_comments(offset)
    if not data:
        break

    all_comments.extend(data)
    offset += 40

    print("取得:", offset)

    # 👇 最小待機（超重要）
    time.sleep(0.1)

print("保存中...")

with open("comments.json", "w", encoding="utf-8") as f:
    json.dump(all_comments, f, ensure_ascii=False)

print("✅ 完了:", len(all_comments))
