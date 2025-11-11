from view.add_dialog import AddHabitDialog
from PyQt6.QtWidgets import QMessageBox, QAbstractItemView, QHeaderView, QProgressBar
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import QSortFilterProxyModel, Qt
from sqlite3 import IntegrityError

class MyHabitsController:
    def __init__(self, window, model):
        self.window = window
        self.model = model
        self.table_model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()

        self.init_ui()
        self.show_habits()

    def init_ui(self):
        # Подключение кнопок
        self.window.AddHabitBtn.clicked.connect(self.add_btn)
        self.window.DeleteHabitBtn.clicked.connect(self.delete_btn)
        self.window.MarkHabitBtn.clicked.connect(self.mark_btn)
        self.window.SearchInput.textChanged.connect(self.get_search_filter)
        self.window.DeleteFilterBtn.clicked.connect(self.remove_filter)
        self.window.FilterBox.activated.connect(self.category_filter)

        # делаем изменения для виджета отображения
        self.window.HabitsTable.setModel(self.table_model)
        self._make_some_changes_to_HabitsTable()
        self.proxy_model.setSourceModel(self.table_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(0)  # фильтр по названию привычки (0-й столбец)
        self.window.HabitsTable.setModel(self.proxy_model)
        

    def add_btn(self):
        dialog = AddHabitDialog(self.window)
        if dialog.exec():
            data = dialog.get_data()
            name = data["name"].strip()
            if not name:
                QMessageBox.warning(self.window, "Ошибка", "Введите название привычки.")
                return
            try:
                self.model.add_habit(
                    name=name,
                    category=data["category"].strip(),
                    frequency=data["daily_frequency"]
                )
                self.show_habits()
            except IntegrityError:
                QMessageBox.warning(self.window, "Ошибка", "Имена привычек не должны повторятся")

    def delete_btn(self):
        current_index = self.window.HabitsTable.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self.window, "Ошибка", "Выберите привычку для удаления.")
            return

        # Преобразуем индекс из proxy в source
        source_index = self.proxy_model.mapToSource(current_index)
        row = source_index.row()

        habit_name = self.table_model.item(row, 0).text()
        self.model.remove_habit(habit_name)
        self.table_model.removeRow(row)

    def mark_btn(self):
        current_index = self.window.HabitsTable.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self.window, "Ошибка", "Выберите привычку для отметки.")
            return

        # Преобразуем индекс из proxy_model в исходный
        source_index = self.proxy_model.mapToSource(current_index)

        row = source_index.row()
        habit_name = self.table_model.item(row, 0).text()
        if self.model.is_habit_completed_today(habit_name):
            QMessageBox.warning(self.window, "Информация", "Эта привычка уже выполнена сегодня.")
            return
        # Меняем отметку в БД
        self.model.toggle_mark_habit(habit_name)

        # Обновляем отображение
        self.show_habits()

    def remove_filter(self):
        self.window.SearchInput.clear()
        self.proxy_model.setFilterFixedString("")
        self.window.FilterBox.setCurrentIndex(0)

    def show_habits(self):
        habits = self.model.get_habits()

        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(["Название", "Категория", "Частота", "Дата", "Выполнено"])

        for habit in habits:
            progress, target = self.model.get_progress_and_target(habit["name"])
            row = [
                QStandardItem(habit["name"]),
                QStandardItem(habit["category"]),
                QStandardItem(str(habit["daily_frequency"])),
                QStandardItem(habit["created_at"]),
                QStandardItem(f"{progress}/{target}" if progress < target else f"✅") 
            ]

            self.table_model.appendRow(row)

        # Растягиваем колонки для наилучшего вида
        header = self.window.HabitsTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, self.table_model.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        # Обновляем категории для FilterBox
        self.update_categories()

    def get_search_filter(self):
        text = self.window.SearchInput.text()
        self.proxy_model.setFilterFixedString(text)

    def category_filter(self):
        """Применяет фильтр по выбранной категории."""
        category = self.window.FilterBox.currentText()  # Получаем выбранную категорию

        if category == "Все":
            # Убираем фильтрацию по категории
            self.proxy_model.setFilterKeyColumn(-1)
            self.proxy_model.setFilterFixedString("")
        else:
            self.proxy_model.setFilterKeyColumn(1)  # Предполагаем, что категории находятся во втором столбце (индекс 1)
            self.proxy_model.setFilterFixedString(category)

    def _make_some_changes_to_HabitsTable(self):
        # отключаем редактирование
        self.window.HabitsTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # выделяем строку целиком
        self.window.HabitsTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # двойной клик для получения информации о привычке
        self.window.HabitsTable.doubleClicked.connect(self.on_habit_double_clicked)

    def on_habit_double_clicked(self, index):
        row = index.row()
        habit_name = self.table_model.item(row, 0).text()
        category = self.table_model.item(row, 1).text()
        frequency = self.table_model.item(row, 2).text()
        marked = self.table_model.item(row, 4).text()
        QMessageBox.information(
            self.window,
            "Выбор привычки",
            f"Вы выбрали привычку:\n\n🧩 {habit_name}\n📂 Категория: {category}\n⏱ Частота: {frequency}\n Выполнена: "
            f"{marked}"
        )

    def update_categories(self):
        """Обновляет пул категорий в FilterBox"""
        categories = self.model.get_categories()
        self.window.FilterBox.clear()
        self.window.FilterBox.addItem("Все")
        self.window.FilterBox.addItems(categories)
        self.window.FilterBox.setCurrentIndex(0)