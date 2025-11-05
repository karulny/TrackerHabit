import pyqtgraph as pg
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import Qt
from datetime import datetime


class StatisticController:
    def __init__(self, window, model):
        self.window = window
        self.model = model

        # Настраиваем layout для графика
        self.layout = QVBoxLayout(self.window.GraphWidget)

        # Создаём сам график
        self.graph = pg.PlotWidget()
        self.graph.setBackground('w')
        self.graph.showGrid(x=True, y=True, alpha=0.3)
        self.graph.setLabel('left', 'Прогресс')
        self.graph.setLabel('bottom', 'Дата')
        self.layout.addWidget(self.graph)

        # Если есть layout для статистики — вставляем туда
        if hasattr(self.window, "statisticLayout"):
            self.window.statisticLayout.addWidget(self.window.GraphWidget)

        # Инициализация UI
        self.init_ui()

    # --- ИНИЦИАЛИЗАЦИЯ ЭЛЕМЕНТОВ ---
    def init_ui(self):
        """Подключает сигналы и заполняет список привычек"""
        self.init_habits()
        self.init_text_time_box()

        # При выборе привычки — автоматически обновляем график
        self.window.HabitBox.currentIndexChanged.connect(self.collect_data_and_call_graph)
        # При смене диапазона времени — автоматически обновляем график
        self.window.TimeBox.currentIndexChanged.connect(self.collect_data_and_call_graph)
        # Кнопка "Обновить" тоже оставляем на случай
        self.window.UpdateGraphBtn.clicked.connect(self.init_habits)

    def init_habits(self):
        """Заполняет выпадающий список привычек"""
        self.window.HabitBox.clear()  # очищаем, чтобы не дублировать
        habits = [habit["name"] for habit in self.model.get_habits()]
        if habits:
            self.window.HabitBox.addItems(habits)
            self.window.HabitBox.setCurrentIndex(0)
        else:
            self.window.HabitBox.addItem("Нет привычек")

    def init_text_time_box(self):
        self.window.TimeBox.addItems(["за день", "за месяц"])
        self.window.TimeBox.setCurrentIndex(0)

    # --- ОТОБРАЖЕНИЕ ГРАФИКА ---
    def plot_habit_progress(self, graph_widget, habit_data, habit_name, month=True):
        """
        Строит график прогресса привычки.
        :param graph_widget: PlotWidget из PyQt для отображения графика
        :param habit_data: Список кортежей (progress, target, date) из get_habit_static_daily
        :param habit_name: Название привычки (для заголовка)
        """
        if not habit_data:
            graph_widget.clear()
            graph_widget.setTitle("Нет данных для отображения")
            return

        # Преобразуем даты и данные
        dates = []
        progress = []
        target = []
        for p, t, d in habit_data:
            if isinstance(d, str):
                d = datetime.strptime(d, "%Y-%m-%d")
            dates.append(d)
            progress.append(p)
            target.append(t)

        x_values = [d.timestamp() for d in dates]

        # Очищаем график
        graph_widget.clear()

        # Линия прогресса
        graph_widget.plot(
            x_values, progress,
            pen=pg.mkPen('b', width=2),
            symbol='o', symbolBrush='b',
            name="Прогресс"
        )

        # Линия цели
        graph_widget.plot(
            x_values, target,
            pen=pg.mkPen('r', style=Qt.PenStyle.DashLine, width=2),
            name="Цель"
        )

        # Настраиваем подписи оси X как дни
        ax = graph_widget.getAxis('bottom')
        ax.setTicks([[(x_values[i], dates[i].strftime("%d.%m")) for i in range(len(dates))]])

        # Заголовок
        graph_widget.setTitle(f"Динамика привычки: {habit_name}")

    def collect_data_and_call_graph(self):
        graph_widget = self.graph
        habit_name = self.window.HabitBox.currentText()
        text_from_time_box = self.window.TimeBox.currentText()
        if text_from_time_box == "за день":
            habit_data = self.model.get_habit_static_daily(habit_name)
            month = False
        else:
            habit_data = self.model.get_habit_static_daily(habit_name)
            month = True
        self.plot_habit_progress(graph_widget, habit_data, habit_name, month)
