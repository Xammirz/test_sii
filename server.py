import sqlite3
from datetime import datetime
from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import os

# Подключение к базе данных SQLite (checklist.db)
checklist_conn = sqlite3.connect('checklist.db', check_same_thread=False)

# Подключение к базе данных SQLite (data.db)
data_conn = sqlite3.connect('static/data/data.db', check_same_thread=False)

# Создание таблицы (если она ещё не создана) в checklist.db
checklist_conn.execute('CREATE TABLE IF NOT EXISTS completed_tasks (date TEXT, dealer_id INTEGER, task_id INTEGER)')

# Создание таблицы (если она ещё не создана) в data.db
data_conn.execute('CREATE TABLE IF NOT EXISTS dealers (id TEXT, last_modified TEXT)')

# Функция для сохранения выполненной задачи в базе данных
def save_completed_task(dealer_id, task_id):
    # Получение текущей даты и времени
    now = datetime.now()
    date_string = now.strftime('%Y-%m-%d %H:%M:%S')

    # Вставка данных в таблицу (checklist.db)
    checklist_conn.execute('INSERT INTO completed_tasks (date, dealer_id, task_id) VALUES (?, ?, ?)', (date_string, dealer_id, task_id))

    # Сохранение изменений в базе данных (checklist.db)
    checklist_conn.commit()

    # Обновление значения поля last_modified в таблице dealers (data.db)
    data_conn.execute('UPDATE dealers SET last_modified = ? WHERE id = ?', (now.strftime('%Y-%m-%d %H:%M:%S'), dealer_id))

    # Сохранение изменений в базе данных (data.db)
    data_conn.commit()

# Функция для удаления выполненной задачи из базы данных
def remove_completed_task(dealer_id, task_id):
    # Удаление записи из таблицы (checklist.db)
    checklist_conn.execute('DELETE FROM completed_tasks WHERE dealer_id = ? AND task_id = ?', (dealer_id, task_id))

    # Сохранение изменений в базе данных (checklist.db)
    checklist_conn.commit()

    # Обновление значения поля last_modified в таблице dealers (data.db)
    data_conn.execute('UPDATE dealers SET last_modified = NULL WHERE id = ?', (dealer_id,))

    # Сохранение изменений в базе данных (data.db)
    data_conn.commit()


# Создание экземпляра FastAPI
app = FastAPI()

# Настройки CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the static directory
static_dir = os.path.join(current_dir, "static")

# Mount the static routes
app.mount("/static", StaticFiles(directory=os.path.join(static_dir)), name="static")


# Route for serving the index.html file
@app.get("/", response_class=HTMLResponse)
async def get_client_page():
    index_path = ("index.html")
    with open(index_path) as f:
        return f.read()

# Маршрут для сохранения значения чеклиста
@app.post("/save_checklist")
async def save_checklist(data: dict = Body(...)):
    dealer_id = data.get('dealerId')
    item_id = data.get('itemId')

    if dealer_id is None or item_id is None:
        return {"status": "error", "message": "Missing required parameters"}

    save_completed_task(dealer_id, item_id)

    return {"status": "success"}

# Маршрут для удаления значения чеклиста
@app.post("/remove_checklist")
async def remove_checklist(data: dict = Body(...)):
    dealer_id = data.get('dealerId')
    item_id = data.get('itemId')

    if dealer_id is None or item_id is None:
        return {"status": "error", "message": "Missing required parameters"}

    remove_completed_task(dealer_id, item_id)

    return {"status": "success"}


# Запуск сервера FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
