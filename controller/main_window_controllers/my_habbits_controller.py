
class MyHabitsController:
    def __init__(self, window):
        self.window = window
        self.init_ui()

    def init_ui(self):
        self.window.AddHabbitBtn.clicked.connect(self.add_btn)
        self.window.DeleteHabbitBtn.clicked.connect(self.delete_btn)
        self.window.MarkHabbitBtn.clicked.connect(self.mark_btn)
        self.window.SearchInput.textChanged.connect(self.get_search_filter)
        self.window.DeleteFilterBtn.clicked.connect(self.delete_btn)

    def add_btn(self):
        pass

    def delete_btn(self):
        self.window.SearchInput.clear()

    def mark_btn(self):
        pass

    def remove_filter(self):
        pass

    def show_habits(self):
        pass

    def get_search_filter(self):
        print('Cool!')

    def get_time_filter(self):
        pass

    def show_time_filter(self):
        pass