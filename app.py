#C言語の#include的なやつ
from flask import Flask, render_template, request, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import log

app = Flask(__name__) #Flaskアプリを作っているnameはファイル名的な

### データベース設定
#セッション用
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

#データベース設定
os.makedirs(app.instance_path, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()
migrate = Migrate()
db.init_app(app)
migrate.init_app(app, db)

##モデルの定義
#ユーザーモデル
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

#タスクモデル
class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)

#login_manager設定
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

#user_loader設定
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
########################

#新規会員登録
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            return "そのメールは既に登録されています", 400

        user = User(
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("index"))

    return render_template("register.html")

#ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            return "メールかパスワードが違います", 400

        login_user(user)
        return redirect(url_for("index"))

    return render_template("login.html")

#ログアウト
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


#htmlを作成&タスク追加
@app.route('/', methods=['GET', 'POST']) #関数に対する設定'/'はトップページのURL、GET:ページを開く,POST:フォームから何かを送信されたとき
@login_required
def index(): #関数の定義,トップページが開かれたときに呼ばれる
    if request.method == "POST":
        task = request.form.get("task")
        if task:
            new_task = Task(name=task, done=False, user_id=current_user.id)
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for("index"))
    db_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.id.asc()).all()
    return render_template("index.html", tasks=db_tasks)

#チェックボックス状態切り替え
@app.route('/toggle/<int:task_id>', methods=['POST'])
@login_required
def toggle(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.done = not task.done
    db.session.commit()
    return redirect(url_for('index'))

#タスク削除
@app.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

#タスク編集
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        new_name = request.form.get('task', '').strip()
        if new_name:
            task.name = new_name
            db.session.commit()
        return redirect(url_for('index'))
        # GETリクエスト時は新しい編集画面を表示
    return render_template('edit.html', task=task)

###エラーハンドリング
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
