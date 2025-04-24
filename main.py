# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.template_folder = 'templates'
app.static_folder = 'static'

# Пути к файлам
USERS_FILE = 'data/users.txt'
PROJECTS_FILE = 'data/projects.txt'

# Создаем папку data если ее нет
os.makedirs('data', exist_ok=True)

# Создаем файлы если их нет
for file in [USERS_FILE, PROJECTS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            f.write('')

from routes import *

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)