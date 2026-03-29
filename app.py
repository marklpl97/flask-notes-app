from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import models
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))   # для flash и сессий

# Инициализация базы данных
models.init_db()

# Контекстный процессор – делает переменную current_user доступной во всех шаблонах
@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    user = None
    if user_id:
        user = models.get_user_by_id(user_id)
    return dict(current_user=user)

# ---------------------- МАРШРУТЫ ----------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm = request.form['confirm']

        if not username or not password:
            flash('Имя пользователя и пароль обязательны', 'error')
        elif password != confirm:
            flash('Пароли не совпадают', 'error')
        elif models.get_user_by_username(username):
            flash('Пользователь с таким именем уже существует', 'error')
        else:
            models.create_user(username, password)
            flash('Регистрация успешна! Теперь войдите.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = models.get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            flash('Вы успешно вошли', 'success')
            return redirect(url_for('notes'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли', 'success')
    return redirect(url_for('index'))

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if not session.get('user_id'):
        flash('Пожалуйста, войдите, чтобы видеть заметки', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        text = request.form['text'].strip()
        if text:
            models.add_note(session['user_id'], text)
            flash('Заметка добавлена', 'success')
        else:
            flash('Заметка не может быть пустой', 'error')
        return redirect(url_for('notes'))

    user_notes = models.get_notes_by_user(session['user_id'])
    return render_template('notes.html', notes=user_notes)

@app.route('/delete_note/<int:note_id>')
def delete_note(note_id):
    if not session.get('user_id'):
        flash('Необходимо войти', 'error')
        return redirect(url_for('login'))
    if models.delete_note(note_id, session['user_id']):
        flash('Заметка удалена', 'success')
    else:
        flash('Заметка не найдена', 'error')
    return redirect(url_for('notes'))

@app.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if not session.get('user_id'):
        flash('Пожалуйста, войдите', 'error')
        return redirect(url_for('login'))

    # Получаем заметку
    note = models.get_note_by_id(note_id)
    if not note or note['user_id'] != session['user_id']:
        flash('Заметка не найдена', 'error')
        return redirect(url_for('notes'))

    if request.method == 'POST':
        text = request.form['text'].strip()
        if text:
            models.update_note(note_id, text)
            flash('Заметка обновлена', 'success')
            return redirect(url_for('notes'))
        else:
            flash('Заметка не может быть пустой', 'error')
            # остаёмся на странице редактирования
            return render_template('edit_note.html', note=note)

    # GET-запрос – показываем форму
    return render_template('edit_note.html', note=note)

if __name__ == '__main__':
    app.run(debug=True)
