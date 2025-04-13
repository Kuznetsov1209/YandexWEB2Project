from flask import Flask, request, redirect, url_for, session
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Необходимо для работы сессий

# Пути к файлам
USERS_FILE = 'users.txt'
PROJECTS_FILE = 'projects.txt'

# Создаем файлы, если их нет
for file in [USERS_FILE, PROJECTS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            f.write('')


def get_page(content):
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Учебные проекты</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f9;
            color: #333;
        }}
        .navbar {{
            background-color: #007bff;
            padding: 15px;
            display: flex;
            justify-content: space-between;
        }}
        .navbar a {{
            color: white;
            text-decoration: none;
            margin: 0 15px;
        }}
        .content {{
            padding: 20px;
            max-width: 800px;
            margin: 20px auto;
            text-align: center;
        }}
        .btn {{
            background-color: #28a745;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin: 10px 5px;
        }}
        .btn-secondary {{
            background-color: #6c757d;
        }}
        .btn-danger {{
            background-color: #dc3545;
        }}
        .btn-container {{
            margin-top: 20px;
        }}
        .alert {{
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid transparent;
            border-radius: 4px;
        }}
        .alert-success {{
            color: #3c763d;
            background-color: #dff0d8;
            border-color: #d6e9c6;
        }}
        .alert-danger {{
            color: #721c24;
            background-color: #f8d7da;
            border-color: #f5c6cb;
        }}
        form {{
            max-width: 500px;
            margin: 0 auto;
            text-align: left;
        }}
        input, textarea {{
            width: 100%;
            padding: 8px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .user-info {{
            color: white;
            margin-right: 15px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/">Учебные проекты</a>
        <div>
            {'<span class="user-info">' + session.get('user_name', '') + '</span>' if 'user_email' in session else ''}
            <a href="/">Главная</a>
            <a href="/about">О проекте</a>
            {'<a href="/logout">Выйти</a>' if 'user_email' in session else '<a href="/login">Войти</a>'}
        </div>
    </div>

    <div class="content">
        {content}
    </div>
</body>
</html>
"""


def save_user(name, email, password):
    """Сохраняет данные пользователя в файл"""
    with open(USERS_FILE, 'a') as f:
        f.write(f"{name},{email},{generate_password_hash(password)}\n")


def user_exists(email):
    """Проверяет, существует ли пользователь с таким email"""
    if not os.path.exists(USERS_FILE):
        return False

    with open(USERS_FILE, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(',')
                if len(parts) >= 2 and parts[1] == email:
                    return True
    return False


def authenticate_user(email, password):
    """Аутентифицирует пользователя"""
    if not os.path.exists(USERS_FILE):
        return False

    with open(USERS_FILE, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(',')
                if len(parts) >= 3 and parts[1] == email:
                    if check_password_hash(parts[2], password):
                        return parts[0]  # Возвращаем имя пользователя
    return False


def save_project(title, description, author_email):
    """Сохраняет проект в файл"""
    with open(PROJECTS_FILE, 'a') as f:
        f.write(f"{title}|{description}|{author_email}\n")


@app.route('/')
def home():
    if 'user_email' in session:
        content = f"""
        <h1>Добро пожаловать, {session['user_name']}!</h1>
        <p>Вы вошли как {session['user_email']}</p>

        <div class="btn-container">
            <a href="/new-project" class="btn">Новый проект</a>
        </div>
        """
    else:
        content = """
        <h1>Онлайн-платформа для управления учебными проектами</h1>
        <p>Упрощаем процесс управления проектами для студентов и преподавателей.</p>

        <div class="btn-container">
            <a href="/login" class="btn">Войти</a>
            <a href="/register" class="btn btn-secondary">Зарегистрироваться</a>
        </div>
        """

    content += """
    <div style="margin-top: 30px;">
        <a href="/about" class="btn">Узнать больше о проекте</a>
    </div>
    """
    return get_page(content)


@app.route('/about')
def about():
    content = """
    <h1>О проекте</h1>
    <p>Проект разработал Кузнецов Макар.</p>
    <p>Проект нужен для автоматизации процесса управления учебными проектами в образовательных учреждениях.</p>
    <p>Основные функции:</p>
    <ul style="text-align: left; max-width: 600px; margin: 0 auto;">
        <li>Создание и отслеживание проектов</li>
        <li>Распределение задач между участниками</li>
        <li>Контроль сроков выполнения</li>
    </ul>
    <div style="margin-top: 20px;">
        <a href="/" class="btn">На главную</a>
    </div>
    """
    return get_page(content)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_email' in session:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_name = authenticate_user(email, password)
        if user_name:
            session['user_email'] = email
            session['user_name'] = user_name
            return redirect(url_for('home'))
        else:
            message = '<div class="alert alert-danger">Неверный email или пароль</div>'

    content = f"""
    <h1>Вход в систему</h1>
    {message}
    <form method="POST" style="max-width: 400px; margin: 0 auto; text-align: left;">
        <div style="margin-bottom: 15px;">
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email" style="width: 100%; padding: 8px;" required>
        </div>
        <div style="margin-bottom: 15px;">
            <label for="password">Пароль:</label><br>
            <input type="password" id="password" name="password" style="width: 100%; padding: 8px;" required>
        </div>
        <button type="submit" class="btn" style="width: 100%;">Войти</button>
    </form>
    <div style="margin-top: 20px;">
        <a href="/" class="btn btn-secondary">На главную</a>
    </div>
    """
    return get_page(content)


@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_email' in session:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if user_exists(email):
            message = '<div class="alert alert-danger">Пользователь с таким email уже зарегистрирован!</div>'
        else:
            save_user(name, email, password)
            message = f'<div class="alert alert-success">Пользователь {name} успешно зарегистрирован!</div>'
            return redirect(url_for('login'))

    content = f"""
    <h1>Регистрация</h1>
    {message}
    <form method="POST" style="max-width: 400px; margin: 0 auto; text-align: left;">
        <div style="margin-bottom: 15px;">
            <label for="name">Имя:</label><br>
            <input type="text" id="name" name="name" style="width: 100%; padding: 8px;" required>
        </div>
        <div style="margin-bottom: 15px;">
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email" style="width: 100%; padding: 8px;" required>
        </div>
        <div style="margin-bottom: 15px;">
            <label for="password">Пароль:</label><br>
            <input type="password" id="password" name="password" style="width: 100%; padding: 8px;" required>
        </div>
        <button type="submit" class="btn" style="width: 100%;">Зарегистрироваться</button>
    </form>
    <div style="margin-top: 20px;">
        <a href="/" class="btn btn-secondary">На главную</a>
    </div>
    """
    return get_page(content)


@app.route('/new-project', methods=['GET', 'POST'])
def new_project():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    message = ''
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        if title and description:
            save_project(title, description, session['user_email'])
            message = '<div class="alert alert-success">Проект успешно создан!</div>'
            # Можно перенаправить на страницу проекта или оставить на этой странице
        else:
            message = '<div class="alert alert-danger">Заполните все поля!</div>'

    content = f"""
    <h1>Создать новый проект</h1>
    {message}
    <form method="POST">
        <div style="margin-bottom: 15px;">
            <label for="title">Название проекта:</label><br>
            <input type="text" id="title" name="title" required>
        </div>
        <div style="margin-bottom: 15px;">
            <label for="description">Описание проекта:</label><br>
            <textarea id="description" name="description" rows="4" required></textarea>
        </div>
        <button type="submit" class="btn">Создать проект</button>
    </form>
    <div style="margin-top: 20px;">
        <a href="/" class="btn btn-secondary">На главную</a>
    </div>
    """
    return get_page(content)


if __name__ == '__main__':
    app.run(debug=True)
