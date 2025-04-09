from flask import Flask

app = Flask(__name__)


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
        .btn-container {{
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/">Учебные проекты</a>
        <div>
            <a href="/">Главная</a>
            <a href="/about">О проекте</a>
            <a href="#">Контакты</a>
        </div>
    </div>

    <div class="content">
        {content}
    </div>
</body>
</html>
"""


@app.route('/')
def home():
    content = """
    <h1>Онлайн-платформа для управления учебными проектами</h1>
    <p>Упрощаем процесс управления проектами для студентов и преподавателей.</p>

    <div class="btn-container">
        <a href="/login" class="btn">Войти</a>
        <a href="/register" class="btn btn-secondary">Зарегистрироваться</a>
    </div>

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


@app.route('/login')
def login():
    content = """
    <h1>Вход в систему</h1>
    <form style="max-width: 400px; margin: 0 auto; text-align: left;">
        <div style="margin-bottom: 15px;">
            <label for="email">Email:</label><br>
            <input type="email" id="email" style="width: 100%; padding: 8px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label for="password">Пароль:</label><br>
            <input type="password" id="password" style="width: 100%; padding: 8px;">
        </div>
        <button type="submit" class="btn" style="width: 100%;">Войти</button>
    </form>
    <div style="margin-top: 20px;">
        <a href="/" class="btn btn-secondary">На главную</a>
    </div>
    """
    return get_page(content)


@app.route('/register')
def register():
    content = """
    <h1>Регистрация</h1>
    <form style="max-width: 400px; margin: 0 auto; text-align: left;">
        <div style="margin-bottom: 15px;">
            <label for="name">Имя:</label><br>
            <input type="text" id="name" style="width: 100%; padding: 8px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label for="email">Email:</label><br>
            <input type="email" id="email" style="width: 100%; padding: 8px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label for="password">Пароль:</label><br>
            <input type="password" id="password" style="width: 100%; padding: 8px;">
        </div>
        <button type="submit" class="btn" style="width: 100%;">Зарегистрироваться</button>
    </form>
    <div style="margin-top: 20px;">
        <a href="/" class="btn btn-secondary">На главную</a>
    </div>
    """
    return get_page(content)


if __name__ == '__main__':
    app.run(debug=True)