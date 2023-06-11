import sqlite3
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def generate_chart_and_save_pdf():
    # Подключение к базе данных SQLite
    conn = sqlite3.connect('checklist.db')
    cursor = conn.cursor()

    # Получение данных о выполненных задачах
    cursor.execute('SELECT date, dealer_id, task_id FROM completed_tasks')
    rows = cursor.fetchall()

    # Создание словаря для хранения информации о количестве выполненных задач по дням для каждого дилера
    data = {}

    # Обработка каждой строки результата запроса
    for row in rows:
        date, dealer_id, task_id = row
        date = date[:10]  # Извлечение только даты из поля date

        # Если дилер уже есть в словаре, увеличиваем счетчик выполненных задач
        if dealer_id in data:
            if date in data[dealer_id]:
                data[dealer_id][date] += 1
            else:
                data[dealer_id][date] = 1
        # Если дилера нет в словаре, добавляем его и инициализируем счетчик выполненных задач
        else:
            data[dealer_id] = {date: 1}

    # Создание графика
    fig, ax = plt.subplots()

    # Обработка данных для каждого дилера
    for dealer_id, dates in data.items():
        x = list(dates.keys())
        y = list(dates.values())

        # Построение графика для каждого дилера
        ax.plot(x, y, label=dealer_id)

    # Настройка осей и легенды графика
    ax.set_xlabel('Дата')
    ax.set_ylabel('Количество выполненных задач')
    ax.legend()

    # Создание PDF-файла с графиком
    with PdfPages('work_chart.pdf') as pdf:
        pdf.savefig(fig)

    # Закрытие соединения с базой данных
    conn.close()

    print('График работы сотрудников сохранен в файле work_chart.pdf')
