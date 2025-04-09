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
        }}
        .btn {{
            background-color: #28a745;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/">Главная</a>
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
    <a href="/about" class="btn">Узнать больше</a>
    """
    return get_page(content)


@app.route('/about')
def about():
    content = """
    <h1>О проекте</h1>
    <p>Проект разработал Кузнецов Макар.</p>
    <p>Проект нужен для автоматизации процесса управления учебными проектами в образовательных учреждениях.</p>
    <p>Основные функции:</p>
    <ul>
        <li>Создание и отслеживание проектов</li>
        <li>Распределение задач между участниками</li>
        <li>Контроль сроков выполнения</li>
    </ul>
    <a href="/" class="btn">На главную</a>
    """
    return get_page(content)


if __name__ == '__main__':
    app.run(debug=True)
