import pyqtgraph as pg
from PyQt6.QtWidgets import QBoxLayout


class StatisticController:
    def __init__(self, window, model):
        self.window = window
        self.model = model

        self.graph = pg.PlotWidget()
        self.graph.setWindowTitle('Привычки')
        self.graph.setBackground("grey")
        self.graph.setParent(window.GraphWidget)

        self.init_ui()

    def init_ui(self):
        self.window.UpdateStaticBtn.clicked.connect(self.update_btn)

    def update_btn(self):
        pass

    def update_graph(self):
        pass
