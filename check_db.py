from app import app, Task

with app.app_context():
    tasks = Task.query.all()
    print("DB tasks count:", len(tasks))
    for t in tasks[:5]:
        print(t.id, t.name, t.done)
