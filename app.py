from flask import Flask, render_template, request, redirect, url_for #C言語の#include的なやつ
import json
import os
import log

app = Flask(__name__) #Flaskアプリを作っているnameはファイル名的な

TASK_FILE = 'tasks.json'


#タスクをjsonファイルから読み込む関数
def load_tasks():
    try:
        if os.path.exists(TASK_FILE):
            with open(TASK_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading tasks: {e}")
        return []

#タスクをjsonファイルに保存する関数
def save_tasks(tasks):
    try:
        with open(TASK_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving tasks: {e}")

#初期化
tasks = load_tasks()

#htmlを作成&タスク追加
@app.route('/', methods=['GET', 'POST']) #関数に対する設定'/'はトップページのURL、GET:ページを開く,POST:フォームから何かを送信されたとき
def index(): #関数の定義,トップページが開かれたときに呼ばれる
    if request.method == "POST":
        task = request.form.get("task")
        if task:
            tasks.append({"name": task, "done": False})
            save_tasks(tasks)
        return redirect(url_for("index"))
    return render_template("index.html", tasks=tasks)

#チェックボックス状態切り替え
@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle(task_id):
    if 0 <= task_id < len(tasks):
        tasks[task_id]["done"] = not tasks[task_id]["done"]
        save_tasks(tasks)
        return redirect(url_for('index'))

#タスク削除
@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    if 0 <= task_id < len(tasks):
        del tasks[task_id]
        save_tasks(tasks)
    return redirect(url_for('index'))

#タスク編集
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    if 0 <= task_id < len(tasks):
        if request.method == 'POST':
            new_name = request.form.get('task')
            if new_name:
                tasks[task_id]['name'] = new_name
                save_tasks(tasks)
            return redirect(url_for('index'))
        # GETリクエスト時は新しい編集画面を表示
        return render_template('edit.html', task=tasks[task_id], task_id=task_id)
    return redirect(url_for('index'))

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
#確認