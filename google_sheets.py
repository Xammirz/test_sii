import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Настройки авторизации
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('ключ.json', scope)
client = gspread.authorize(creds)

# Открываем таблицу
sheet = client.open('название таблицы').sheet1

# Получаем данные из таблицы и преобразуем их в словарь
data = {}
for row in sheet.get_all_records():
    city_name = row['name']
    dealers = []
    for dealer_id, dealer_name, dealer_address, dealer_checklist, dealer_last_modified in zip(row['id'], row['name'], row['address'], row['checklist'], row['last_modified']):
        dealer = {
            'id': dealer_id,
            'name': dealer_name,
            'address': dealer_address,
            'checklist': dealer_checklist,
            'last_modified': dealer_last_modified
        }
        dealers.append(dealer)
    data[city_name] = dealers

# Сохраняем данные в файл json
with open('data/daata.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# Записываем chat_id в файл .env
chat_id_col = sheet.col_values(sheet.find('chat_id').col)
chat_id_values = chat_id_col[1:]  # Пропускаем заголовок столбца

with open('.env', 'w') as f:
    for i, chat_id in enumerate(chat_id_values):
        f.write(f'chat_id_{i+1}={chat_id}\n')
