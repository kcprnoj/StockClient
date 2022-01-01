import sys
from pandas.core.frame import DataFrame
import qdarkstyle
from PyQt5.QtWidgets import QApplication, QDateEdit, QListWidget, QComboBox, QSizePolicy, QTableView, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit
from PyQt5.QtCore import QAbstractTableModel, QDateTime, Qt
from PyQt5.QtGui import QIcon
from Controller import Controller
import mplfinance as mpf
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from style import style

class ClientView(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1200, 800)
        self.setWindowTitle('Client Stock App')
        self.setWindowIcon(QIcon('logo.png'))
        self.module_object = None
        self.model = None
        self.controller = Controller()
        self.companies = []

        self.layout = QVBoxLayout()

        self.comboIndexes = QComboBox()
        self.comboIndexes.addItems(self.controller.get_indexes())
        self.comboIndexes.currentIndexChanged.connect(self.update_index)
        self.layout.addWidget(self.comboIndexes)

        self.search = QLineEdit()
        self.search.textChanged.connect(self.search_items)
        self.search.setPlaceholderText('Search')
        self.layout.addWidget(self.search)

        layoutLabels = QHBoxLayout()
        self.layout.addLayout(layoutLabels)

        self.label_equities = QLabel('Equities: ')
        self.label_equities.setMaximumWidth(200)
        self.label_equity= QLabel('Equity information: ')
        layoutLabels.addWidget(self.label_equities)
        layoutLabels.addWidget(self.label_equity)

        self.layoutEquitiesWidgets = QHBoxLayout()
        self.layout.addLayout(self.layoutEquitiesWidgets)

        self.listWidgetEquities = QListWidget()
        self.listWidgetEquities.verticalScrollBar().setStyleSheet('width: 10px')
        self.listWidgetEquities.setMaximumWidth(200)
        self.listWidgetEquities.itemSelectionChanged.connect(self.update_equities)
        self.layoutEquitiesWidgets.addWidget(self.listWidgetEquities)

        self.layoutEquity = QVBoxLayout()

        self.table = QTableView()
        self.table.setMaximumHeight(60)
        self.layoutEquity.addWidget(self.table)
        self.canvas = None

        label_start = QLabel('Start date: ')
        label_end = QLabel('End date: ')
        label_type = QLabel('Plot type: ')
        layoutPlotLabels = QHBoxLayout()
        layoutPlotLabels.addWidget(label_start)
        layoutPlotLabels.addWidget(label_end)
        layoutPlotLabels.addWidget(label_type)
        layoutPlotLabels.setAlignment(Qt.AlignTop)
        self.layoutEquity.addLayout(layoutPlotLabels)

        layoutControls = QHBoxLayout()
        self.dateStart = QDateEdit(calendarPopup=True)
        self.dateStart.setDateTime(QDateTime.currentDateTime().addMonths(-2))
        self.dateStart.dateChanged.connect(self.update_plot)
        self.dateEnd = QDateEdit(calendarPopup=True)
        self.dateEnd.setDateTime(QDateTime.currentDateTime())
        self.dateEnd.dateChanged.connect(self.update_plot)
        layoutControls.addWidget(self.dateStart)
        layoutControls.addWidget(self.dateEnd)
        self.comboType = QComboBox()
        self.comboType.addItems(['candle','ohlc', 'line','renko','pnf','hollow_and_filled'])
        self.comboType.currentIndexChanged.connect(self.update_plot)
        layoutControls.addWidget(self.comboType)
        layoutControls.setAlignment(Qt.AlignTop)
        self.layoutEquity.addLayout(layoutControls)

        self.layoutEquitiesWidgets.addLayout(self.layoutEquity)

        layoutStatus = QHBoxLayout()
        self.status = QLabel()
        appVersion = QLabel('Autor: Kacper Nojszewski')
        layoutStatus.addWidget(self.status)
        layoutStatus.addWidget(appVersion, alignment=Qt.AlignRight)
        self.layout.addLayout(layoutStatus)
        self.setLayout(self.layout)

        self.update_index()

    def update_equities(self):
        data = self.controller.get_company(self.listWidgetEquities.currentItem().text())
        self.table.setModel(TableModel(data))
        self.update_plot()

    def update_plot(self):
        data = self.controller.get_historical(self.listWidgetEquities.currentItem().text(), start = self.dateStart.text(), end = self.dateEnd.text())
        if data is None:
            return
        if self.canvas != None:
            self.layoutEquity.removeWidget(self.canvas)
            self.canvas.setParent(None)
        fig, axlist = mpf.plot(data, type=self.comboType.currentText(), show_nontrading=False, xrotation=0, \
                                datetime_format='%d/%m/%Y', returnfig=True, style = style, volume=True, tight_layout = True)
        self.canvas = FigureCanvasQTAgg(fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layoutEquity.addWidget(self.canvas)

    def update_index(self):
        self.companies = self.controller.get_index_companies(self.comboIndexes.currentText())['Name'].tolist()
        self.listWidgetEquities.clear()
        self.listWidgetEquities.addItems(self.companies)
        self.search_items()

    def search_items(self):
        self.listWidgetEquities.clear()
        for company in self.companies:
            if self.search.text() in company.lower():
                self.listWidgetEquities.addItem(company)

class TableModel(QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])

if __name__ == '__main__':
    app = QApplication(sys.argv)

    clientView = ClientView()
    clientView.setStyleSheet(qdarkstyle.load_stylesheet())
    clientView.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Exiting')