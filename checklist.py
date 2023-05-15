import sqlite3
from datetime import datetime

# Подключаемся к базе данных
conn = sqlite3.connect('checklist.db')

# Создаем таблицу для хранения выполненных задач
conn.execute('CREATE TABLE IF NOT EXISTS completed_tasks (date TEXT, dealer_id INTEGER, task_id INTEGER)')

# Функция для сохранения выполненной задачи в базе данных
def save_completed_task(dealer_id, task_id):
    # Получаем текущую дату и время
    now = datetime.now()
    date_string = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # Вставляем данные в таблицу
    conn.execute('INSERT INTO completed_tasks (date, dealer_id, task_id) VALUES (?, ?, ?)', (date_string, dealer_id, task_id))
    
    # Сохраняем изменения в базе данных
    conn.commit()
