import http.server
import sqlite3
import json
from datetime import datetime

# Подключение к базе данных
conn = sqlite3.connect('checklist.db')

# Создание таблицы (если она ещё не создана)
conn.execute('CREATE TABLE IF NOT EXISTS completed_tasks (date TEXT, dealer_id INTEGER, task_id INTEGER)')

# Функция для сохранения выполненной задачи в базе данных
def save_completed_task(dealer_id, task_id):
    # Получение текущей даты и времени
    now = datetime.now()
    date_string = now.strftime('%Y-%m-%d %H:%M:%S')

    # Вставка данных в таблицу
    conn.execute('INSERT INTO completed_tasks (date, dealer_id, task_id) VALUES (?, ?, ?)', (date_string, dealer_id, task_id))

    # Сохранение изменений в базе данных
    conn.commit()

# Функция для получения выполненных задач за текущий день
def get_completed_tasks():
    # Получение текущей даты и времени
    now = datetime.now()
    date_string = now.strftime('%Y-%m-%d')

    # Выполнение запроса к базе данных
    cursor = conn.execute('SELECT task_id FROM completed_tasks WHERE date LIKE ?', (date_string + '%',))
    tasks = [row[0] for row in cursor.fetchall()]

    return tasks

# Класс обработчика запросов
class RequestHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        # Проверка пути запроса
        if self.path == '/save_checklist':
            # Получение данных из тела запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            checklist_values = json.loads(post_data.decode('utf-8'))

            # Сохранение значений чеклиста в базе данных
            for value in checklist_values:
                save_completed_task(value['dealerId'], value['itemId'])

            # Отправка ответа
            self._set_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
        else:
            self._set_headers(status_code=404)
            self.wfile.write(json.dumps({'status': 'error', 'message': 'Not found'}).encode('utf-8'))

# Запуск сервера
def run(server_class=http.server.HTTPServer, handler_class=RequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    print('Starting server...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
