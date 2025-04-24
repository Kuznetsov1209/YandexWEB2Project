import http.server
import socketserver
import webbrowser
import os

# Указываем порт для сервера
PORT = 8000

# Меняем текущую директорию на ту, где находится скрипт
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Создаем HTTP-сервер
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Сервер запущен на http://localhost:{PORT}")
    print("Открываю браузер...")
    # Открываем браузер с указанной ссылкой
    webbrowser.open_new_tab(f"http://localhost:{PORT}")
    try:
        # Запускаем сервер
        print("Для остановки сервера нажмите Ctrl+C.")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")