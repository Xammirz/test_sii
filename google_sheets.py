import datetime
import time
import json
import os
import sys

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

# Ключ службы в JSON-формате.
KEY_FILE_LOCATION = 'data/key_file.json'

# Идентификатор электронной таблицы Google.
SPREADSHEET_ID = '1GfxxSBTwR5jGV49oyyfkur_m_2hwF8YV1GooZLqU31Q'

# Диапазон ячеек, содержащих данные.
RANGE_NAME = 'A2:E'

# Время, в которое вы хотите запускать скрипт.
HOUR_OF_DAY = 12
MINUTE_OF_HOUR = 0


def main():
    # Аутентификация с использованием ключа службы.
    credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION,
                                                                   ['https://www.googleapis.com/auth/spreadsheets.readonly'])

    # Создание объекта API для доступа к Google Sheets.
    service = build('sheets', 'v4', credentials=credentials)

    # Получение данных из электронной таблицы.
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
    values = result.get('values', [])

    # Формирование словаря с данными.
    data = {
        "cities": [],
        "dealers": {}
    }
    city_id = 1
    for row in values:
        city_name = row[0]
        dealer_name = row[1]
        dealer_address = row[2]
        dealer_checklist = row[3].split(',') if len(row) > 3 else []
        dealer_last_modified = row[4] if len(row) > 4 else 'здесь пока вас не было'

        # Проверяем, есть ли уже город в списке городов.
        city = next((c for c in data["cities"] if c["name"] == city_name), None)
        if city is None:
            city = {"id": f"city_{city_id}", "name": city_name}
            data["cities"].append(city)
            data["dealers"][city["id"]] = []
            city_id += 1

        # Добавляем дилера в список дилеров города.
        dealer_id = len(data["dealers"][city["id"]])
        dealer = {
            "id": dealer_id,
            "name": dealer_name,
            "address": dealer_address,
            "checklist": dealer_checklist,
            "last_modified": dealer_last_modified
        }
        data["dealers"][city["id"]].append(dealer)

    # Сохранение данных в файле JSON.
    current_datetime = datetime.datetime.now()
    filename = 'data/data.json'
    file_path = os.path.join(os.getcwd(), filename)
    with open(file_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


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
