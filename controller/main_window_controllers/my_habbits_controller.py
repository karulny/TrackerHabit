from view.add_dialog import AddHabitDialog
from PyQt6.QtWidgets import QMessageBox, QAbstractItemView, QHeaderView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
# QRegularExpression вроде не используется, но решил оставить так как в Qt документации, это штучка нужна для сортировки QproxyFilterModel
# это я так понял, в теории онва правда может и не нужна, но лучше оставить чтобы избежать багов в будущем
from PyQt6.QtCore import QSortFilterProxyModel, Qt, QRegularExpression
from sqlite3 import IntegrityError


class CustomFilterProxyModel(QSortFilterProxyModel):
    """Кастомная прокси-модель для фильтрации по нескольким столбцам стандартная QT-шная не позволяет сделать фильтр более чем по двум"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.name_filter = ""
        self.category_filter = ""

    def set_name_filter(self, text):
        """Устанавливает фильтр по названию"""
        self.name_filter = text.lower()
        self.invalidateFilter()

    def set_category_filter(self, text):
        """Устанавливает фильтр по категории"""
        self.category_filter = text
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """Переопределенный метод для фильтрации по обоим критериям"""
        model = self.sourceModel()
        
        # Получаем данные из нужных столбцов
        name_index = model.index(source_row, 0, source_parent)
        category_index = model.index(source_row, 1, source_parent)
        
        name = model.data(name_index, Qt.ItemDataRole.DisplayRole)
        category = model.data(category_index, Qt.ItemDataRole.DisplayRole)
        
        # Проверяем фильтр по названию
        name_match = True
        if self.name_filter:
            name_match = self.name_filter in name.lower() if name else False
        
        # Проверяем фильтр по категории
        category_match = True
        if self.category_filter and self.category_filter != "Все":
            category_match = (category == self.category_filter) if category else False
        
        # Строка проходит фильтр только если оба условия выполнены
        return name_match and category_match


class MyHabitsController:
    """Контроллер вкладки привычек"""
    def __init__(self, window, model):
        self.window = window
        self.model = model
        # Ставим модели для работы с таблицей
        self.table_model = QStandardItemModel()
        # Используем кастомную модель
        self.proxy_model = CustomFilterProxyModel()  

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
        self.proxy_model.setSourceModel(self.table_model)
        self.window.HabitsTable.setModel(self.proxy_model)
        self._make_some_changes_to_HabitsTable()

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
        """Сбрасывает все фильтры"""
        self.window.SearchInput.clear()
        self.window.FilterBox.setCurrentIndex(0)
        # Сбрасываем оба фильтра
        self.proxy_model.set_name_filter("")
        self.proxy_model.set_category_filter("")

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
        
        # Растягиваем строки по вертикали для лучшего отображения, иначе из-за qss стиля цифры будут 'зажованы'
        vertical_header = self.window.HabitsTable.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Обновляем категории для FilterBox
        self.update_categories()

    def get_search_filter(self):
        """Применяет фильтр поиска по названию привычки"""
        text = self.window.SearchInput.text()
        self.proxy_model.set_name_filter(text)

    def category_filter(self):
        """Применяет фильтр по выбранной категории"""
        category = self.window.FilterBox.currentText()
        self.proxy_model.set_category_filter(category)

    def _make_some_changes_to_HabitsTable(self):
        # отключаем редактирование
        self.window.HabitsTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # выделяем строку целиком
        self.window.HabitsTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # двойной клик для получения информации о привычке
        self.window.HabitsTable.doubleClicked.connect(self.on_habit_double_clicked)

    def on_habit_double_clicked(self, index):
        """Обработчик двойного клика по строке"""
        # ВАЖНО: преобразуем proxy индекс в source индекс
        source_index = self.proxy_model.mapToSource(index)
        row = source_index.row()
        
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
        current_category = self.window.FilterBox.currentText()
        
        self.window.FilterBox.clear()
        self.window.FilterBox.addItem("Все")
        self.window.FilterBox.addItems(categories)
        
        # Пытаемся восстановить выбранную категорию
        index = self.window.FilterBox.findText(current_category)
        if index >= 0:
            self.window.FilterBox.setCurrentIndex(index)
        else:
            self.window.FilterBox.setCurrentIndex(0)