from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QHBoxLayout

class AddHabitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить привычку")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название привычки")
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.name_input)

        self.category_input = QLineEdit()
        layout.addWidget(QLabel("Категория:"))
        layout.addWidget(self.category_input)

        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["Ежедневно", "Раз в неделю", "Раз в месяц"])
        layout.addWidget(QLabel("Частота:"))
        layout.addWidget(self.frequency_combo)

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
            "category": self.category_input.text(),
            "frequency": self.frequency_combo.currentText()
        }
