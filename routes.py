from flask import render_template, request, redirect, url_for, session, flash
from server import app, USERS_FILE, PROJECTS_FILE
import os
from werkzeug.security import generate_password_hash, check_password_hash


def save_user(name, email, password, role='student'):
    with open(USERS_FILE, 'a') as f:
        f.write(f"{name},{email},{generate_password_hash(password)},{role}\n")


def user_exists(email):
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
    project_id = str(len(open(PROJECTS_FILE).readlines()) + 1)
    with open(PROJECTS_FILE, 'a') as f:
        f.write(f"{project_id}|{title}|{description}|{author_email}\n")
    return project_id


def get_user_projects(email):
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
        return render_template('home.html',
                               user_name=session['user_name'],
                               user_email=session['user_email'],
                               teacher_buttons=teacher_buttons)
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')



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
            message = 'Неверный email или пароль'
            return render_template('login.html', message=message)

    return render_template('login.html')


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
            message = 'Пользователь с таким email уже зарегистрирован!'
        else:
            save_user(name, email, password, 'student')
            return redirect(url_for('login'))

    return render_template('register.html', message=message)


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
            message = 'Неверный код доступа для учителей!'
        elif user_exists(email):
            message = 'Пользователь с таким email уже зарегистрирован!'
        else:
            save_user(name, email, password, 'teacher')
            return redirect(url_for('login'))

    return render_template('register_teacher.html', message=message)


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
            message = 'Заполните все поля!'

    return render_template('new_project.html', message=message)


@app.route('/project-created')
def project_created():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('project_created.html')


@app.route('/my-projects')
def my_projects():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    projects = get_user_projects(session['user_email'])
    return render_template('my_projects.html', projects=projects)


@app.route('/delete-project/<project_id>')
def delete_project_route(project_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))

    if delete_project(project_id, session['user_email']):
        message = 'Проект успешно удален!'
    else:
        message = 'Не удалось удалить проект'

    return render_template('my_projects.html',
                           projects=get_user_projects(session['user_email']),
                           message=message)


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
                message = 'Не удалось обновить проект'
        else:
            message = 'Заполните все поля!'

    return render_template('edit_project.html', project=project, message=message)


@app.route('/manage-students')
def manage_students():
    if 'user_email' not in session or not session.get('is_teacher'):
        return redirect(url_for('home'))

    students = get_all_students()
    return render_template('manage_students.html', students=students)


@app.route('/view-student-projects/<student_email>')
def view_student_projects(student_email):
    if 'user_email' not in session or not session.get('is_teacher'):
        return redirect(url_for('home'))

    projects = get_user_projects(student_email)
    return render_template('view_student_projects.html',
                           student_email=student_email,
                           projects=projects)
