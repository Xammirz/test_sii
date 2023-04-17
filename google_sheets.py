import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, time, timedelta

# настройки таблицы
sheet_name = "Имя таблицы"
worksheet_name = "Название листа"
city_col = 1  # номер столбца с городами
dealer_col = 2  # номер столбца с дилерами
address_col = 3  # номер столбца с адресами

# настройки авторизации
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "data/data.json",
    ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
)
client = gspread.authorize(creds)

# получаем таблицу и лист
sheet = client.open(sheet_name)
worksheet = sheet.worksheet(worksheet_name)

# получаем данные из таблицы
cities = worksheet.col_values(city_col)
dealers = worksheet.col_values(dealer_col)
addresses = worksheet.col_values(address_col)

# удаляем заголовки столбцов
cities.pop(0)
dealers.pop(0)
addresses.pop(0)

# создаем словарь для данных
data = {}

# заполняем словарь данными из таблицы
for i in range(len(cities)):
    city = cities[i]
    dealer = dealers[i]
    address = addresses[i]

    if city not in data:
        data[city] = []

    data[city].append({"dealer": dealer, "address": address})

# сохраняем данные в JSON файл
filename = "data.json"
with open(filename, "w") as f:
    json.dump(data, f, indent=4)

# расписание обновления данных
update_time = time(hour=0, minute=0)  # время обновления: 12 ночи МСК
current_time = datetime.utcnow().time()

if current_time < update_time:
    # обновляем данные в запланированное время
    update_delta = datetime.combine(datetime.utcnow().date(), update_time) - datetime.utcnow()
    update_seconds = update_delta.total_seconds()
    print(f"Next update in {update_seconds / 60:.1f} minutes")
    time.sleep(update_seconds)
else:
    # обновляем данные сразу, если уже прошло запланированное время
    print("Updating data now...")

# обновляем данные и сохраняем в JSON файл
# повторяем код, начиная с строки `# получаем таблицу и лист`
# и заканчивая строкой `json.dump(data, f, indent=4)`
