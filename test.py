import requests
import json

url = 'http://localhost:8000/save_checklist'
data = [
    {'dealerId': 1, 'itemId': 1},
    {'dealerId': 2, 'itemId': 3},
    {'dealerId': 1, 'itemId': 2},
]

response = requests.post(url, data=json.dumps(data))
if 'error' in response.json():
    print('Произошла ошибка:', response.json()['error'])
else:
    print('Запрос выполнен успешно')
    print(response.json())

