import requests
import json
import time

# 🔧 ここにスタジオIDを入れる
STUDIO_ID = "51471940"

all_comments = []

offset = 0
limit = 40

def fetch_comments():
    global offset

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
            add_comment(c)
            fetch_replies(c)

        offset += limit
        time.sleep(0.5)  # API制限対策

def add_comment(c, parent_id=None):
    all_comments.append({
        "id": c.get("id"),
        "content": c.get("content"),
        "datetime_created": c.get("datetime_created"),
        "author": c.get("author"),
        "parent_id": parent_id
    })

def fetch_replies(comment):
    # 🔥 repliesがある場合
    if "replies" in comment and comment["replies"]:
        for r in comment["replies"]:
            add_comment(r, parent_id=comment["id"])

            # 🔥 もし将来ネストが増えても対応（安全設計）
            if "replies" in r and r["replies"]:
                fetch_replies(r)

def main():
    fetch_comments()

    # 🔥 時間順ソート（超重要）
    all_comments.sort(key=lambda x: x["datetime_created"])

    with open("comments.json", "w", encoding="utf-8") as f:
        json.dump(all_comments, f, ensure_ascii=False, indent=2)

    print(f"保存完了: {len(all_comments)}件")

if __name__ == "__main__":
    main()
