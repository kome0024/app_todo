from app import app, db, Task

with app.app_context():
    Task.query.delete()
    db.session.commit()
    print("tasksテーブルを全削除しました")
