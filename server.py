# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, url_for, session
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
port = int(os.environ.get("PORT", 3000))

# Пути к файлам
USERS_FILE = 'data/users.txt'
PROJECTS_FILE = 'data/projects.txt'

# Создаем файлы, если их нет
os.makedirs('data', exist_ok=True)
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
        .btn-warning {{
            background-color: #ffc107;
            color: black;
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
        .teacher-badge {{
            background-color: #ffc107;
            color: black;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/">Учебные проекты</a>
        <div>
            {'<span class="user-info">' + session.get('user_name', '') +
             ('<span class="teacher-badge">Учитель</span>' if session.get('is_teacher') else '') +
             '</span>' if 'user_email' in session else ''}
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


def save_user(name, email, password, role='student'):
    """Сохраняет данные пользователя в файл"""
    with open(USERS_FILE, 'a') as f:
        f.write(f"{name},{email},{generate_password_hash(password)},{role}\n")


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
        return None

    with open(USERS_FILE, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(',')
                if len(parts) >= 4 and parts[1] == email:
                    if check_password_hash(parts[2], password):
                        return {
                            'name': parts[0],
                            'email': parts[1],
                            'is_teacher': parts[3] == 'teacher'
                        }
    return None


def save_project(title, description, author_email):
    """Сохраняет проект в файл"""
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


def get_all_students():
    """Получает список всех студентов"""
    students = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) >= 4 and parts[3] == 'student':
                        students.append({
                            'name': parts[0],
                            'email': parts[1]
                        })
    return students


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
        teacher_buttons = ""
        if session.get('is_teacher'):
            teacher_buttons = """
            <div class="btn-container">
                <a href="/manage-students" class="btn btn-warning">Управление студентами</a>
            </div>
            """

        content = f"""
        <h1>Добро пожаловать, {session['user_name']}!</h1>
        <p>Вы вошли как {session['user_email']}</p>
        {teacher_buttons}
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
            <a href="/register" class="btn btn-secondary">Регистрация студента</a>
            <a href="/register-teacher" class="btn btn-warning">Регистрация учителя</a>
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
        <li>Разделение прав доступа для студентов и учителей</li>
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

        user = authenticate_user(email, password)
        if user:
            session['user_email'] = user['email']
            session['user_name'] = user['name']
            session['is_teacher'] = user['is_teacher']
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
    session.pop('is_teacher', None)
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
            save_user(name, email, password, 'student')
            message = f'<div class="alert alert-success">Студент {name} успешно зарегистрирован!</div>'
            return redirect(url_for('login'))

    content = f"""
    <h1>Регистрация студента</h1>
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


@app.route('/register-teacher', methods=['GET', 'POST'])
def register_teacher():
    if 'user_email' in session:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        secret_code = request.form.get('secret_code', '')

        if secret_code != "TEACHER123":
            message = '<div class="alert alert-danger">Неверный код доступа для учителей!</div>'
        elif user_exists(email):
            message = '<div class="alert alert-danger">Пользователь с таким email уже зарегистрирован!</div>'
        else:
            save_user(name, email, password, 'teacher')
            message = f'<div class="alert alert-success">Учитель {name} успешно зарегистрирован!</div>'
            return redirect(url_for('login'))

    content = f"""
    <h1>Регистрация учителя</h1>
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
        <div style="margin-bottom: 15px;">
            <label for="secret_code">Секретный код:</label><br>
            <input type="password" id="secret_code" name="secret_code" style="width: 100%; padding: 8px;" required>
        </div>
        <button type="submit" class="btn btn-warning" style="width: 100%;">Зарегистрироваться как учитель</button>
    </form>
    <div style="margin-top: 20px;">
        <a href="/" class="btn btn-secondary">На главную</a>
    </div>
    """
    return get_page(content)


@app.route('/manage-students')
def manage_students():
    if 'user_email' not in session or not session.get('is_teacher'):
        return redirect(url_for('home'))

    students = get_all_students()
    students_html = ""

    for student in students:
        students_html += f"""
        <div class="project-card">
            <h3>{student['name']}</h3>
            <p>{student['email']}</p>
            <div class="project-actions">
                <a href="/view-student-projects/{student['email']}" class="btn">Просмотреть проекты</a>
            </div>
        </div>
        """

    content = f"""
    <h1>Управление студентами</h1>
    {students_html if students else '<p>Нет зарегистрированных студентов</p>'}
    <div style="margin-top: 20px;">
        <a href="/" class="btn btn-secondary">На главную</a>
    </div>
    """
    return get_page(content)


@app.route('/view-student-projects/<student_email>')
def view_student_projects(student_email):
    if 'user_email' not in session or not session.get('is_teacher'):
        return redirect(url_for('home'))

    projects = get_user_projects(student_email)
    projects_html = ""

    for project in projects:
        projects_html += f"""
        <div class="project-card">
            <h3>{project['title']}</h3>
            <p>{project['description']}</p>
        </div>
        """

    content = f"""
    <h1>Проекты студента {student_email}</h1>
    {projects_html if projects else '<p>У студента пока нет проектов</p>'}
    <div style="margin-top: 20px;">
        <a href="/manage-students" class="btn btn-secondary">Назад к списку студентов</a>
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