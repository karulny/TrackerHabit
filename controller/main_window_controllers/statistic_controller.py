import pyqtgraph as pg
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import Qt
from datetime import datetime, date


class StatisticController:
    def __init__(self, window, model):
        self.window = window
        self.model = model

        # Настраиваем layout для графика
        self.layout = QVBoxLayout(self.window.GraphWidget)

        # Создаём сам график
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('w')
        self.layout.addWidget(self.graph_widget)

        # Если есть layout для статистики — вставляем туда
        if hasattr(self.window, "statisticLayout"):
            self.window.statisticLayout.addWidget(self.window.GraphWidget)

        # Инициализация UI
        self.init_ui()

    # --- ИНИЦИАЛИЗАЦИЯ ЭЛЕМЕНТОВ ---
    def init_ui(self):
        """Подключает сигналы и заполняет список привычек"""
        self.init_text_time_box()
        self.update_habits()
        # При выборе привычки — автоматически обновляем график
        self.window.HabitBox.currentIndexChanged.connect(self.collect_data_and_call_graph)
        # При смене диапазона времени — автоматически обновляем график
        self.window.TimeBox.currentIndexChanged.connect(self.collect_data_and_call_graph)
        # Кнопка "Обновить" тоже оставляем на случай
        self.window.UpdateGraphBtn.clicked.connect(self.collect_data_and_call_graph)

    def update_habits(self):
        """Заполняет выпадающий список привычек"""
        print("Обновлен")
        self.window.HabitBox.clear()  # очищаем, чтобы не дублировать
        habits = [habit["name"] for habit in self.model.get_habits()]
        if habits:
            self.window.HabitBox.addItems(habits)
            self.window.HabitBox.setCurrentIndex(0)
        else:
            self.window.HabitBox.addItem("Нет привычек")
        

    def init_text_time_box(self):
        self.window.TimeBox.addItems(["За сегодня", "за 7 дней", "за 30 дней"])
        self.window.TimeBox.setCurrentIndex(0)

            # --- ОТОБРАЖЕНИЕ ГРАФИКА ---
    def plot_habit_progress(self, habit_data):
        """Строит график прогресса привычки."""
        self.graph_widget.clear()

        dates = []
        completed = []

        for item in habit_data:
            print(item)
            # Безопасная распаковка
            if isinstance(item, (tuple, list)) and len(item) == 2:
                d, c = item
            else:
                # Пропускаем любые некорректные записи
                continue

            # Фильтруем нули
            if c <= 0:
                continue

            # Преобразуем дату
            try:
                if " " in d:
                    dt = datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
                else:
                    dt = datetime.strptime(d, "%Y-%m-%d")
            except ValueError:
                continue

            # Форматируем дату для графика
            if dt.date() == date.today():
                dates.append(dt.strftime("%H:%M:%S"))
            else:
                dates.append(dt.strftime("%d.%m.%Y"))

            completed.append(c)

        # Если после фильтрации нет данных — график не строим
        if not dates:
            return

        x = list(range(len(dates)))

        bg = pg.BarGraphItem(x=x, height=completed, width=0.6, brush='g')
        self.graph_widget.addItem(bg)

        ax = self.graph_widget.getAxis('bottom')
        ax.setTicks([list(zip(x, dates))])

        self.graph_widget.setYRange(-0.5, 1.5)
        self.graph_widget.setLabel('left', 'Выполнено (1) / Не выполнено (0)')
        self.graph_widget.setLabel('bottom', 'Дата')
        self.graph_widget.setTitle("Статистика привычки")
        self.graph_widget.showGrid(x=True, y=True)


    def collect_data_and_call_graph(self):
        habit_name = self.window.HabitBox.currentText()
        if self.window.TimeBox.currentIndex() == 0:
            habit_data = self.model.get_habit_static_daily(habit_name)
        else:
            text_from_time_box = self.window.TimeBox.currentText()
            days = text_from_time_box.split()[1]
            habit_data = self.model.get_habit_static_for_N_days(habit_name, days)
        
        
        self.plot_habit_progress(habit_data)