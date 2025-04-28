# Импорт необходимых модулей Flask и других библиотек
from flask import render_template, request, redirect, url_for, session, flash
from server import app, USERS_FILE, PROJECTS_FILE  # Импорт основного приложения и путей к файлам
import os  # Для работы с файловой системой
from werkzeug.security import generate_password_hash, check_password_hash  # Для хеширования паролей


# Функция для сохранения нового пользователя
def save_user(name, email, password, role='student'):
    """
    Сохраняет данные пользователя в файл USERS_FILE
    Формат строки: имя,email,хеш_пароля,роль
    """
    with open(USERS_FILE, 'a') as f:  # Открытие файла в режиме добавления
        f.write(f"{name},{email},{generate_password_hash(password)},{role}\n")


# Функция проверки существования пользователя по email
def user_exists(email):
    """Проверяет, есть ли пользователь с указанным email в файле"""
    if not os.path.exists(USERS_FILE):  # Если файла нет, пользователей нет
        return False
    with open(USERS_FILE, 'r') as f:
        for line in f:
            if line.strip():  # Пропускаем пустые строки
                parts = line.strip().split(',')
                if len(parts) >= 2 and parts[1] == email:  # Проверяем email (второе поле)
                    return True
    return False


# Функция аутентификации пользователя
def authenticate_user(email, password):
    """Проверяет email и пароль, возвращает данные пользователя или None"""
    if not os.path.exists(USERS_FILE):
        return None
    with open(USERS_FILE, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(',')
                # Проверяем email и хеш пароля
                if len(parts) >= 4 and parts[1] == email:
                    if check_password_hash(parts[2], password):
                        return {
                            'name': parts[0],
                            'email': parts[1],
                            'is_teacher': parts[3] == 'teacher'  # Проверка роли
                        }
    return None


# Функция сохранения проекта
def save_project(title, description, author_email):
    """Сохраняет проект в файл PROJECTS_FILE"""
    project_id = str(len(open(PROJECTS_FILE).readlines()) + 1)  # Генерация ID
    with open(PROJECTS_FILE, 'a') as f:
        # Формат: ID|название|описание|email автора
        f.write(f"{project_id}|{title}|{description}|{author_email}\n")
    return project_id


# Функция получения проектов пользователя
def get_user_projects(email):
    """Возвращает список проектов конкретного пользователя"""
    projects = []
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    # Проверяем email автора (четвертое поле)
                    if len(parts) >= 4 and parts[3] == email:
                        projects.append({
                            'id': parts[0],
                            'title': parts[1],
                            'description': parts[2]
                        })
    return projects


# Функция получения всех студентов
def get_all_students():
    """Возвращает список всех студентов (пользователей с ролью 'student')"""
    students = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(',')
                    # Проверяем роль (четвертое поле)
                    if len(parts) >= 4 and parts[3] == 'student':
                        students.append({
                            'name': parts[0],
                            'email': parts[1]
                        })
    return students


# Функция удаления проекта
def delete_project(project_id, user_email):
    """Удаляет проект по ID, если текущий пользователь - автор"""
    if not os.path.exists(PROJECTS_FILE):
        return False
    lines = []
    deleted = False
    with open(PROJECTS_FILE, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split('|')
                # Ищем проект с указанным ID и email автора
                if len(parts) >= 4 and parts[0] == project_id and parts[3] == user_email:
                    deleted = True  # Помечаем для удаления
                else:
                    lines.append(line)  # Сохраняем остальные проекты
    if deleted:
        with open(PROJECTS_FILE, 'w') as f:
            f.writelines(lines)  # Перезаписываем файл без удаленного проекта
    return deleted


# Маршрут главной страницы
@app.route('/')
def home():
    """Главная страница с разным контентом для авторизованных/неавторизованных"""
    if 'user_email' in session:  # Если пользователь вошел
        teacher_buttons = ""
        if session.get('is_teacher'):  # Дополнительные кнопки для учителей
            teacher_buttons = """
            <div class="btn-container">
                <a href="/manage-students" class="btn btn-warning">Управление студентами</a>
            </div>
            """
        return render_template('home.html',
                               user_name=session['user_name'],
                               user_email=session['user_email'],
                               teacher_buttons=teacher_buttons)
    return render_template('home.html')  # Стандартный вид для неавторизованных


# Маршрут страницы "О проекте"
@app.route('/about')
def about():
    """Страница с информацией о проекте"""
    return render_template('about.html')


# Маршрут входа в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Обработка входа пользователя"""
    if 'user_email' in session:  # Если уже авторизован - на главную
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':  # Обработка формы входа
        email = request.form['email']
        password = request.form['password']

        user = authenticate_user(email, password)
        if user:  # Если аутентификация успешна
            session['user_email'] = user['email']  # Сохраняем в сессию
            session['user_name'] = user['name']
            session['is_teacher'] = user['is_teacher']
            return redirect(url_for('home'))
        else:
            message = 'Неверный email или пароль'
            return render_template('login.html', message=message)

    return render_template('login.html')


# Маршрут выхода из системы
@app.route('/logout')
def logout():
    """Выход пользователя - очистка сессии"""
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('is_teacher', None)
    return redirect(url_for('home'))


# Маршрут регистрации студента
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового студента"""
    if 'user_email' in session:  # Если уже авторизован - на главную
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if user_exists(email):  # Проверка на существование пользователя
            message = 'Пользователь с таким email уже зарегистрирован!'
        else:
            save_user(name, email, password, 'student')  # Сохранение студента
            return redirect(url_for('login'))

    return render_template('register.html', message=message)


# Маршрут регистрации учителя
@app.route('/register-teacher', methods=['GET', 'POST'])
def register_teacher():
    """Регистрация нового учителя (требуется секретный код)"""
    if 'user_email' in session:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        secret_code = request.form.get('secret_code', '')

        if secret_code != "TEACHER123":  # Проверка секретного кода
            message = 'Неверный код доступа для учителей!'
        elif user_exists(email):
            message = 'Пользователь с таким email уже зарегистрирован!'
        else:
            save_user(name, email, password, 'teacher')  # Сохранение учителя
            return redirect(url_for('login'))

    return render_template('register_teacher.html', message=message)


# Маршрут создания нового проекта
@app.route('/new-project', methods=['GET', 'POST'])
def new_project():
    """Создание нового учебного проекта"""
    if 'user_email' not in session:  # Только для авторизованных
        return redirect(url_for('login'))

    message = ''
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        if title and description:  # Проверка заполнения полей
            save_project(title, description, session['user_email'])
            return redirect(url_for('project_created'))
        else:
            message = 'Заполните все поля!'

    return render_template('new_project.html', message=message)


# Маршрут страницы успешного создания проекта
@app.route('/project-created')
def project_created():
    """Страница подтверждения создания проекта"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('project_created.html')


# Маршрут списка проектов пользователя
@app.route('/my-projects')
def my_projects():
    """Отображение проектов текущего пользователя"""
    if 'user_email' not in session:
        return redirect(url_for('login'))

    projects = get_user_projects(session['user_email'])
    return render_template('my_projects.html', projects=projects)


# Маршрут удаления проекта
@app.route('/delete-project/<project_id>')
def delete_project_route(project_id):
    """Удаление проекта по ID"""
    if 'user_email' not in session:
        return redirect(url_for('login'))

    if delete_project(project_id, session['user_email']):
        message = 'Проект успешно удален!'
    else:
        message = 'Не удалось удалить проект'

    return render_template('my_projects.html',
                           projects=get_user_projects(session['user_email']),
                           message=message)


# Маршрут редактирования проекта
@app.route('/edit-project/<project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    """Редактирование существующего проекта"""
    if 'user_email' not in session:
        return redirect(url_for('login'))

    # Поиск проекта по ID
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

    if not project:  # Если проект не найден или не принадлежит пользователю
        return redirect(url_for('my_projects'))

    message = ''
    if request.method == 'POST':  # Обработка формы редактирования
        title = request.form['title']
        description = request.form['description']

        if title and description:
            lines = []
            updated = False
            # Перезапись файла с обновленными данными
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
                message = 'Не удалось обновить проект'
        else:
            message = 'Заполните все поля!'

    return render_template('edit_project.html', project=project, message=message)


# Маршрут управления студентами (для учителей)
@app.route('/manage-students')
def manage_students():
    """Страница управления студентами (доступна только учителям)"""
    if 'user_email' not in session or not session.get('is_teacher'):
        return redirect(url_for('home'))

    students = get_all_students()
    return render_template('manage_students.html', students=students)


# Маршрут просмотра проектов студента
@app.route('/view-student-projects/<student_email>')
def view_student_projects(student_email):
    """Просмотр проектов конкретного студента (для учителей)"""
    if 'user_email' not in session or not session.get('is_teacher'):
        return redirect(url_for('home'))

    projects = get_user_projects(student_email)
    return render_template('view_student_projects.html',
                           student_email=student_email,
                           projects=projects)
