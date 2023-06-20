import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import calendar
from matplotlib.backends.backend_pdf import PdfPages

# Подключение к базе данных
conn_data = sqlite3.connect('static/data/data.db')
conn_checklist = sqlite3.connect('checklist.db')
cursor_data = conn_data.cursor()
cursor_checklist = conn_checklist.cursor()

# Запрос на выборку данных
cursor_data.execute('SELECT id, address, checklist FROM dealers')
cursor_checklist.execute('SELECT date, dealer_id, COUNT(*) FROM completed_tasks GROUP BY date, dealer_id')

# Получение результатов запросов
dealers = cursor_data.fetchall()
results = cursor_checklist.fetchall()

# Проверка наличия данных
if len(results) == 0:
    print("Нет данных")
else:
    # Создание матрицы для хранения количества задач
    num_dealers = len(dealers)
    num_tasks = len(set(result[2] for result in results))

    # Получение даты и месяца из первой записи
    first_date = results[0][0]
    year, month, _ = map(int, first_date.split('-'))

    # Определение количества дней в месяце
    num_days = calendar.monthrange(year, month)[1]

    # Создание матрицы для хранения количества выполненных задач
    task_counts = np.zeros((num_dealers, num_days), dtype=int)

    # Заполнение матрицы значениями количества выполненных задач
    dealer_dict = {dealer[0]: i for i, dealer in enumerate(dealers)}
    for result in results:
        dealer_id = result[1]
        task_id = result[2]
        dealer_index = dealer_dict[dealer_id]
        date = result[0].split('-')
        day_index = int(date[2]) - 1
        task_counts[dealer_index][day_index] = task_id

    # Построение первого графика (количество выполненных задач по дням и магазинам)
    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(task_counts, cmap='viridis')

    # Настройка осей
    ax.set_xticks(np.arange(num_days))
    ax.set_yticks(np.arange(num_dealers))
    ax.set_xticklabels(np.arange(1, num_days + 1), rotation=45)
    ax.set_yticklabels([dealer[1] for dealer in dealers])
    ax.set_xlabel('Дни')
    ax.set_ylabel('Адреса')
    ax.set_title(f'Отчет сотрудника за\n{calendar.month_name[month]} {year}')

    # Отображение значений в ячейках
    for i in range(num_dealers):
        for j in range(num_days):
            text = ax.text(j, i, task_counts[i][j], ha='center', va='center', color='black')

    # Создание цветовой шкалы
    cbar = ax.figure.colorbar(im, ax=ax, label='Количество выполненных задач')

    # Вывод общего количества задач за месяц и среднего количества задач в день
    total_tasks = np.sum(task_counts)
    average_tasks = total_tasks / num_days
    text_block = f'Общее количество выполненных задач за месяц: {total_tasks}\nСреднее количество задач в день за месяц: {average_tasks}'

    # Автоматическое расположение и подгонка графика
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    # Вывод текстового блока
    plt.figtext(0.5, 0.02, text_block, fontsize=12, ha='center', va='bottom')

    # Сохранение первого графика в PDF файле
    pdf = PdfPages('task_counts_graph.pdf')
    pdf.savefig()

    # Создание второго графика (соответствие магазинов и задач)
    task_names = []
    task_counts_total = []
    for dealer in dealers:
        checklist = dealer[2].split(',')
        task_names.extend(checklist)
        task_counts_total.extend([1] * len(checklist))

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.barh(task_names, task_counts_total)
    ax.set_xlabel('Количество выполненных задач')
    ax.set_ylabel('Название задачи')
    ax.set_title('Статистика задач')

    # Автоматическое расположение и подгонка графика
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    # Сохранение второго графика в PDF файле
    pdf.savefig()

    # Закрытие PDF файла
    pdf.close()

# Закрытие соединения с базами данных
conn_data.close()
conn_checklist.close()
