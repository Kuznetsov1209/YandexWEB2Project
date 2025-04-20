from flask import Flask, request, redirect, url_for, session
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Необходимо для работы сессий
port = int(os.environ.get("PORT", 3000))
# Пути к файлам
USERS_FILE = 'data/users.txt'
PROJECTS_FILE = 'data/projects.txt'

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
        .project-card {{
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
            text-align: left;
        }}
        .project-actions {{
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/">Учебные проекты</a>
        <div>
            {'<span class="user-info">' + session.get('user_name', '') + '</span>' if 'user_email' in session else ''}
            {'<a href="/my-projects">Мои проекты</a>' if 'user_email' in session else ''}
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
                        return parts[0]  # Возвращаем имя  пользователя
    return False


def save_project(title, description, author_email):
    """Сохраняет проект в файл и возвращает ID проекта"""
    project_id = str(len(open(PROJECTS_FILE).readlines()) + 1)
    with open(PROJECTS_FILE, 'a') as f:
        f.write(f"{project_id}|{title}|{description}|{author_email}\n")
    return project_id


def get_user_projects(email):
    """Получает проекты пользователя из файла"""
    projects = []
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 4 and parts[3] == email:
                        projects.append({
                            'id': parts[0],
                            'title': parts[1],
                            'description': parts[2]
                        })
    return projects


def delete_project(project_id, user_email):
    """Удаляет проект пользователя"""
    if not os.path.exists(PROJECTS_FILE):
        return False

    lines = []
    deleted = False
    with open(PROJECTS_FILE, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split('|')
                if len(parts) >= 4 and parts[0] == project_id and parts[3] == user_email:
                    deleted = True
                else:
                    lines.append(line)

    if deleted:
        with open(PROJECTS_FILE, 'w') as f:
            f.writelines(lines)

    return deleted


@app.route('/')
def home():
    if 'user_email' in session:
        content = f"""
        <h1>Добро пожаловать, {session['user_name']}!</h1>
        <p>Вы вошли как {session['user_email']}</p>

        <div class="btn-container">
            <a href="/new-project" class="btn">Новый проект</a>
            <a href="/my-projects" class="btn btn-secondary">Мои проекты</a>
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
            return redirect(url_for('project_created'))
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


@app.route('/project-created')
def project_created():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    content = """
    <h1>Проект успешно создан!</h1>
    <div class="alert alert-success">
        Ваш проект был сохранен в системе. Теперь вы можете:
    </div>

    <div class="btn-container">
        <a href="/my-projects" class="btn">Посмотреть мои проекты</a>
        <a href="/new-project" class="btn">Создать еще один проект</a>
    </div>
    """
    return get_page(content)


@app.route('/my-projects')
def my_projects():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    projects = get_user_projects(session['user_email'])
    projects_html = ""

    for project in projects:
        projects_html += f"""
        <div class="project-card">
            <h3>{project['title']}</h3>
            <p>{project['description']}</p>
            <div class="project-actions">
                <a href="/edit-project/{project['id']}" class="btn">Редактировать</a>
                <a href="/delete-project/{project['id']}" class="btn btn-danger">Удалить</a>
            </div>
        </div>
        """

    content = f"""
    <h1>Мои проекты</h1>
    {projects_html if projects else '<p>У вас пока нет проектов</p>'}
    <div class="btn-container">
        <a href="/new-project" class="btn">Создать новый проект</a>
        <a href="/" class="btn btn-secondary">На главную</a>
    </div>
    """
    return get_page(content)


@app.route('/delete-project/<project_id>')
def delete_project(project_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))

    if delete_project(project_id, session['user_email']):
        message = '<div class="alert alert-success">Проект успешно удален!</div>'
    else:
        message = '<div class="alert alert-danger">Не удалось удалить проект</div>'

    content = f"""
    <h1>Удаление проекта</h1>
    {message}
    <div class="btn-container">
        <a href="/my-projects" class="btn">Вернуться к моим проектам</a>
        <a href="/" class="btn btn-secondary">На главную</a>
    </div>
    """
    return get_page(content)


@app.route('/edit-project/<project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))

    # Находим проект
    project = None
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 4 and parts[0] == project_id and parts[3] == session['user_email']:
                        project = {
                            'id': parts[0],
                            'title': parts[1],
                            'description': parts[2]
                        }
                        break

    if not project:
        return redirect(url_for('my_projects'))

    message = ''
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        if title and description:
            # Обновляем проект
            lines = []
            updated = False
            with open(PROJECTS_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        parts = line.strip().split('|')
                        if len(parts) >= 4 and parts[0] == project_id and parts[3] == session['user_email']:
                            lines.append(f"{project_id}|{title}|{description}|{session['user_email']}\n")
                            updated = True
                        else:
                            lines.append(line)

            if updated:
                with open(PROJECTS_FILE, 'w') as f:
                    f.writelines(lines)
                return redirect(url_for('my_projects'))
            else:
                message = '<div class="alert alert-danger">Не удалось обновить проект</div>'
        else:
            message = '<div class="alert alert-danger">Заполните все поля!</div>'

    content = f"""
    <h1>Редактирование проекта</h1>
    {message}
    <form method="POST">
        <div style="margin-bottom: 15px;">
            <label for="title">Название проекта:</label><br>
            <input type="text" id="title" name="title" value="{project['title']}" required>
        </div>
        <div style="margin-bottom: 15px;">
            <label for="description">Описание проекта:</label><br>
            <textarea id="description" name="description" rows="4" required>{project['description']}</textarea>
        </div>
        <button type="submit" class="btn">Сохранить изменения</button>
    </form>
    <div style="margin-top: 20px;">
        <a href="/my-projects" class="btn btn-secondary">Отмена</a>
    </div>
    """
    return get_page(content)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
