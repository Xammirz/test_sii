import datetime
import time
import os
import sys
import sqlite3
import json
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

# Ключ службы в JSON-формате.
KEY_FILE_LOCATION = 'static/data/key_file.json'

# Идентификатор электронной таблицы Google.
SPREADSHEET_ID = '1GfxxSBTwR5jGV49oyyfkur_m_2hwF8YV1GooZLqU31Q'

# Диапазон ячеек, содержащих данные.
RANGE_NAME = 'A2:G'

# Время, в которое вы хотите запускать скрипт.
HOUR_OF_DAY = 12
MINUTE_OF_HOUR = 0

# Путь к базе данных SQLite.
DATABASE_PATH = 'static/data/data.db'
# Путь к JSON-файлу.
JSON_FILE_PATH = 'static/data/data.json'


def create_tables_if_not_exists(connection):
    cursor = connection.cursor()
    # Создание таблицы cities, если она не существует.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')

    # Создание таблицы dealers, если она не существует.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dealers (
            id TEXT PRIMARY KEY,
            city_id INTEGER,
            name TEXT,
            address TEXT,
            checklist TEXT,
            last_modified TEXT,
            FOREIGN KEY (city_id) REFERENCES cities (id)
        )
    ''')
    connection.commit()


def insert_data(connection, data):
    cursor = connection.cursor()

    # Очистка таблиц перед вставкой новых данных.
    cursor.execute('DELETE FROM cities')
    cursor.execute('DELETE FROM dealers')

    # Вставка данных городов.
    for city in data['cities']:
        city_id = int(city['id'].split('_')[1])  # Преобразование идентификатора в целое число.
        cursor.execute('INSERT INTO cities (id, name) VALUES (?, ?)', (city_id, city['name']))

    # Вставка данных дилеров.
    for city_id, dealers in data['dealers'].items():
        for dealer in dealers:
            cursor.execute(
                'INSERT INTO dealers (id, city_id, name, address, checklist, last_modified) VALUES (?, ?, ?, ?, ?, ?)',
                (dealer['id'], city_id, dealer['name'], dealer['address'], ','.join(dealer['checklist']),
                 dealer['last_modified'])
            )

    connection.commit()


def retrieve_data_from_database(connection):
    cursor = connection.cursor()

    # Извлечение данных городов.
    cursor.execute('SELECT * FROM cities')
    cities = cursor.fetchall()

    # Извлечение данных дилеров.
    cursor.execute('SELECT * FROM dealers')
    dealers = cursor.fetchall()

    # Формирование словаря с данными.
    data = {
        "cities": [],
        "dealers": {}
    }

    # Заполнение данных городов.
    for city in cities:
        city_id, city_name = city
        data["cities"].append({"id": f"city_{city_id}", "name": city_name})

    # Заполнение данных дилеров.
    for dealer in dealers:
        dealer_id, city_id, name, address, checklist, last_modified = dealer
        dealer_data = {
            "id": dealer_id,
            "name": name,
            "address": address,
            "checklist": checklist.split(','),
            "last_modified": last_modified
        }
        if city_id not in data["dealers"]:
            data["dealers"][city_id] = []
        data["dealers"][city_id].append(dealer_data)

    return data


def save_data_as_json(data):
    json_data = {
        "cities": data["cities"],
        "dealers": data["dealers"]
    }
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)


def main():
    # Аутентификация с использованием ключа службы.
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, ['https://www.googleapis.com/auth/spreadsheets.readonly'] # type: ignore
    )

    # Создание объекта API для доступа к Google Sheets.
    service = build('sheets', 'v4', credentials=credentials)

    # Получение данных из электронной таблицы.
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME
    ).execute()
    values = result.get('values', [])

    # Формирование словаря с данными.
    data = {
        "cities": [],
        "dealers": {}
    }
    allowed_chat_ids = []
    city_id = 1
    for row in values:
        if len(row) > 6:
            allowed_chat_ids.append(row[6])

        city_name = row[0]
        dealer_name = row[1]
        dealer_address = row[2]
        dealer_checklist = row[3].split(',') if len(row) > 3 else []
        dealer_last_modified = row[4] if len(row) > 4 else 'здесь пока вас не было'

        # Проверяем, есть ли уже город в списке городов.
        city = next((c for c in data["cities"] if c["name"] == city_name), None)
        if city is None:
            city_id += 1
            city = {"id": f"city_{city_id}", "name": city_name}
            data["cities"].append(city)
            data["dealers"][city["id"]] = []

        # Генерируем уникальный идентификатор дилера.
        dealer_id = f"{city['id']}_{len(data['dealers'][city['id']])}"

        # Добавляем дилера в список дилеров города.
        dealer = {
            "id": dealer_id,
            "name": dealer_name,
            "address": dealer_address,
            "checklist": dealer_checklist,
            "last_modified": dealer_last_modified
        }
        data["dealers"][city["id"]].append(dealer)

    # Сохранение данных в SQLite.
    connection = sqlite3.connect(DATABASE_PATH)
    create_tables_if_not_exists(connection)
    insert_data(connection, data)
    connection.close()

    # Извлечение данных из базы данных.
    connection = sqlite3.connect(DATABASE_PATH)
    data = retrieve_data_from_database(connection)
    connection.close()

    # Сохранение данных в JSON-файле.
    save_data_as_json(data)

    # Сохранение данных в файле .env.
    env_filename = '.env'
    env_file_path = os.path.join(os.getcwd(), env_filename)
    allowed_chat_ids_str = ','.join(allowed_chat_ids)
    with open(env_file_path, 'r') as env_file:
        lines = env_file.readlines()
        env_file.close()

    with open(env_file_path, 'w') as env_file:
        for line in lines:
            if not line.startswith("ALLOWED_CHAT_IDS="):
                env_file.write(line)
        env_file.write(f"ALLOWED_CHAT_IDS={allowed_chat_ids_str}\n")


if __name__ == '__main__':
    # Выполнение скрипта каждые 24 часа в 12:00 по московскому времени.
    if len(sys.argv) > 1 and sys.argv[1] == 'force':
        main()
    else:
        while True:
            now = datetime.datetime.now()
            if now.hour == HOUR_OF_DAY and now.minute == MINUTE_OF_HOUR:
                main()
            time.sleep(60)
