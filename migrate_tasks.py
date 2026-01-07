import json
import os

from app import app, db, Task  # app.py 側に Task モデルがある前提

TASK_FILE = "tasks.json"

def migrate():
    if not os.path.exists(TASK_FILE):
        print("tasks.json が見つかりません")
        return

    with open(TASK_FILE, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    with app.app_context():
        inserted = 0
        skipped = 0

        for t in tasks:
            name = (t.get("name") or "").strip()
            done = bool(t.get("done", False))

            if not name:
                skipped += 1
                continue

            # 同名タスクの重複投入を避けたい場合はここでチェックも可能
            db.session.add(Task(name=name, done=done))
            inserted += 1

        db.session.commit()

    print(f"移行完了: inserted={inserted}, skipped={skipped}")

if __name__ == "__main__":
    migrate()
