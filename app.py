from flask import Flask, render_template, request, redirect, url_for #C言語の#include的なやつ
import log

app = Flask(__name__) #Flaskアプリを作っているnameはファイル名的な

### データベース設定
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate.init_app(app, db)

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)

###




#htmlを作成&タスク追加
@app.route('/', methods=['GET', 'POST']) #関数に対する設定'/'はトップページのURL、GET:ページを開く,POST:フォームから何かを送信されたとき
def index(): #関数の定義,トップページが開かれたときに呼ばれる
    if request.method == "POST":
        task = request.form.get("task")
        if task:
            new_task = Task(name=task, done=False)
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for("index"))
    db_tasks = Task.query.order_by(Task.id.asc()).all()
    return render_template("index.html", tasks=db_tasks)

#チェックボックス状態切り替え
@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle(task_id):
    task = Task.query.get(task_id)
    if task is not None:
        task.done = not task.done
        db.session.commit()
    return redirect(url_for('index'))

#タスク削除
@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    task = Task.query.get(task_id)
    if task is not None:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

#タスク編集
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        new_name = request.form.get('task')
        if new_name:
            task.name = new_name
            db.session.commit()
        return redirect(url_for('index'))
        # GETリクエスト時は新しい編集画面を表示
    return render_template('edit.html', task=task)

#エラーハンドリング
#404エラー
@app.errorhandler(404)
def not_found(error):
    log.logger.error(f"404 error: {error}")
    return render_template("404.html"), 404
#500エラー
@app.errorhandler(500)
def internal_error(error):
    log.logger.error(f"500 error: {error}")
    return render_template("500.html"), 500 

if __name__ == '__main__':
    app.run(debug=True)