import requests
import json
import time
import os

studio_id = "51471940"
STEP = 400
FILE = "comments.json"

if os.path.exists(FILE):
    with open(FILE, "r", encoding="utf-8") as f:
        all_comments = json.load(f)
else:
    all_comments = []

offset = len(all_comments)

def fetch_comments(offset):
    url = f"https://api.scratch.mit.edu/studios/{studio_id}/comments"
    params = {"limit": 40, "offset": offset}
    headers = {"User-Agent": "Mozilla/5.0"}
    return requests.get(url, params=params, headers=headers).json()

print("開始:", offset)

new_comments = []

for i in range(STEP // 40):
    data = fetch_comments(offset)
    if not data:
        break

    new_comments.extend(data)
    offset += 40
    time.sleep(0.3)

all_comments.extend(new_comments)

with open(FILE, "w", encoding="utf-8") as f:
    json.dump(all_comments, f, ensure_ascii=False)

print("完了:", len(all_comments))
