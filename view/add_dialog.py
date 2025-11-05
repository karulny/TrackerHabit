from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QHBoxLayout, QSpinBox

class AddHabitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить привычку")
        self.setMinimumSize(300, 200)

        layout = QVBoxLayout()

        # Название привычки
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название привычки")
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.name_input)

        # Категория привычки
        self.category_input = QComboBox()
        self.category_input.addItems(["Здоровье", "Спорт", "Обучение", "Работа", "Личное развитие", "Другое"])
        self.category_input.setEditable(True)  # Позволяет вводить свою категорию
        layout.addWidget(QLabel("Категория:"))
        layout.addWidget(self.category_input)

        # Частота в день (количество раз)
        self.daily_frequency_spin = QSpinBox()
        self.daily_frequency_spin.setMinimum(1)
        self.daily_frequency_spin.setMaximum(20)
        self.daily_frequency_spin.setValue(1)
        self.daily_frequency_spin.setSuffix(" раз(а)")
        layout.addWidget(QLabel("Количество раз в день:"))
        layout.addWidget(self.daily_frequency_spin)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.accept)

    def get_data(self):
        """Возвращает введённые пользователем данные"""
        return {
            "name": self.name_input.text(),
            "category": self.category_input.currentText(),
            "daily_frequency": self.daily_frequency_spin.value()
        }