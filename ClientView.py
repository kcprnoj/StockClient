import sys
from matplotlib.backends.backend_qt5 import MainWindow
from pandas.core.frame import DataFrame
import qdarkstyle
from PyQt5.QtWidgets import QAction, QApplication, QDateEdit, QErrorMessage, QFileDialog, QListWidget, QComboBox, QMessageBox, QPushButton, QRadioButton, QSizePolicy, QTableView, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit
from PyQt5.QtCore import QAbstractTableModel, QDateTime, QMutex, QObject, QThread, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from Controller import Controller
import mplfinance as mpf
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from style import style
from threading import Thread, current_thread
import matplotlib.pyplot as plt
from qtwidgets import AnimatedToggle

class ClientView(QWidget):
    dataSingal = pyqtSignal()
    companiesSignal = pyqtSignal()
    companySignal = pyqtSignal()
    messageSignal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.resize(1200, 800)
        self.setWindowTitle('Client Stock App')
        self.setWindowIcon(QIcon('logo.png'))

        self.controller = Controller()

        self.messageSignal.connect(self.display_message)

        #Setup signals and mutexes for data
        self.companies = []
        self.companiesMutex = QMutex()
        self.companiesSignal.connect(self.update_companies)

        self.company = None
        self.companyMutex= QMutex()
        self.companySignal.connect(self.update_company)

        self.data = None
        self.dataMutex = QMutex()
        self.dataSingal.connect(self.update_plot)
        self.volume = True

        self.layout = QVBoxLayout()

        self.setup_ui_top()

        self.setup_ui_scroll_list()

        self.setup_ui_equity()

        self.setup_save_data()

        layoutStatus = QHBoxLayout()
        self.status = QLabel()
        appVersion = QLabel('Autor: Kacper Nojszewski')
        layoutStatus.addWidget(self.status)
        layoutStatus.addWidget(appVersion, alignment=Qt.AlignRight)
        self.layout.addLayout(layoutStatus)
        self.setLayout(self.layout)

        self.start_companies()

    def setup_ui_top(self):
        self.comboIndexes = QComboBox()
        self.comboIndexes.addItems(self.controller.get_indexes())
        self.comboIndexes.currentIndexChanged.connect(self.start_companies)
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

    def setup_ui_scroll_list(self):
        self.layoutEquitiesWidgets = QHBoxLayout()
        self.layout.addLayout(self.layoutEquitiesWidgets)

        self.listWidgetEquities = QListWidget()
        self.listWidgetEquities.verticalScrollBar().setStyleSheet('width: 10px')
        self.listWidgetEquities.setMaximumWidth(200)
        self.listWidgetEquities.itemSelectionChanged.connect(self.start_company)
        self.layoutEquitiesWidgets.addWidget(self.listWidgetEquities)

    def setup_ui_equity(self):
        self.layoutEquity = QVBoxLayout()

        self.table = QTableView()
        self.table.setMaximumHeight(60)
        self.layoutEquity.addWidget(self.table)
        self.canvas = None

        #Labels
        label_start = QLabel('Start date: ')
        label_end = QLabel('End date: ')
        label_type = QLabel('Plot type: ')
        label_interval = QLabel('Interval: ')
        layoutPlotLabels = QHBoxLayout()
        layoutPlotLabels.addWidget(label_start)
        layoutPlotLabels.addWidget(label_end)
        layoutPlotLabels.addWidget(label_type)
        layoutPlotLabels.addWidget(label_interval)
        layoutPlotLabels.setAlignment(Qt.AlignTop)
        self.layoutEquity.addLayout(layoutPlotLabels)

        #Date
        layoutControls = QHBoxLayout()
        self.dateStart = QDateEdit(calendarPopup=True)
        self.dateStart.setDateTime(QDateTime.currentDateTime().addMonths(-2))
        self.dateStart.dateChanged.connect(self.start_historical_data)
        self.dateEnd = QDateEdit(calendarPopup=True)
        self.dateEnd.setDateTime(QDateTime.currentDateTime())
        self.dateEnd.dateChanged.connect(self.start_historical_data)
        layoutControls.addWidget(self.dateStart)
        layoutControls.addWidget(self.dateEnd)

        #Plot type
        self.comboType = QComboBox()
        self.comboType.addItems(['candle','ohlc', 'line','renko','pnf','hollow_and_filled'])
        self.comboType.currentIndexChanged.connect(self.update_plot)
        layoutControls.addWidget(self.comboType)
        layoutControls.setAlignment(Qt.AlignTop)
        self.layoutEquity.addLayout(layoutControls)

        #Invterval
        self.comboInterval = QComboBox()
        self.comboInterval.addItems(['1D', '7D', '1M'])
        self.comboInterval.currentIndexChanged.connect(self.start_historical_data)
        layoutControls.addWidget(self.comboInterval)
        layoutControls.setAlignment(Qt.AlignTop)
        self.layoutEquity.addLayout(layoutControls)

        #Buttons
        layoutButtons = QHBoxLayout()
        saveDataButton = QPushButton()
        saveDataButton.clicked.connect(lambda: self.saveFile.triggered.emit())
        saveDataButton.setText("Save data to csv")
        layoutButtons.addWidget(saveDataButton)

        savePlotButton = QPushButton()
        savePlotButton.clicked.connect(lambda: self.savePlot.triggered.emit())
        savePlotButton.setText("Save plot")
        layoutButtons.addWidget(savePlotButton)
        self.layoutEquity.addLayout(layoutButtons)

        label_volume = QLabel('Volume :')
        label_volume.setMaximumWidth(50)
        self.volumeButton = AnimatedToggle(
        bar_color=Qt.darkGray,
        checked_color="#26486B",
        handle_color=Qt.gray,
        )
        self.volumeButton.toggle()
        self.volumeButton.setMaximumWidth(100)
        self.volumeButton.toggled.connect(self.setVolume)
        layoutButtons.addWidget(label_volume)
        layoutButtons.addWidget(self.volumeButton)
        self.layoutEquity.addLayout(layoutButtons)

        self.layoutEquitiesWidgets.addLayout(self.layoutEquity)

    def setup_ui_bottom(self):
        layoutStatus = QHBoxLayout()
        self.status = QLabel()
        appVersion = QLabel('Autor: Kacper Nojszewski')
        layoutStatus.addWidget(self.status)
        layoutStatus.addWidget(appVersion, alignment=Qt.AlignRight)
        self.layout.addLayout(layoutStatus)
        self.setLayout(self.layout)

    def setVolume(self, state):
        self.volume = state
        self.update_plot()

    def setup_save_data(self):
        self.saveFile = QAction("&Save File", self)
        self.saveFile.setStatusTip('Save File')
        self.saveFile.triggered.connect(self.file_save_csv)
        self.savePlot = QAction("&Save Plot", self)
        self.savePlot.setStatusTip('Save Plot')
        self.savePlot.triggered.connect(self.file_save_plot)

    def file_save_plot(self):
        name = QFileDialog.getSaveFileName(self, 'Save Plot', filter = "Text files (*.png)")
        self.dataMutex.lock()
        print(name[0])
        if self.comboType.currentText() != None and self.data is not None and name[0] != '':
            fig, axlist = mpf.plot(self.data, type=self.comboType.currentText(), show_nontrading=False, xrotation=20, \
                        datetime_format='%d/%m/%Y', returnfig=True, volume=self.volume)
            fig.savefig(name[0])
        self.dataMutex.unlock()

    def file_save_csv(self):
        name = QFileDialog.getSaveFileName(self, 'Save File', filter = "Text files (*.csv)")
        print(name)
        self.dataMutex.lock()
        if self.comboType.currentText() != None and self.data is not None and name[0] != '':
            self.data.to_csv(name[0])
        self.dataMutex.unlock()

    def update_company(self):
        self.companyMutex.lock()
        print(current_thread().name + " Updating company")
        self.table.setModel(TableModel(self.company))
        self.start_historical_data()
        self.companyMutex.unlock()

    def update_plot(self):
        self.dataMutex.lock()
        print(current_thread().name + " Updating Plot")
        if self.data is None:
            return
        if self.canvas != None:
            self.layoutEquity.removeWidget(self.canvas)
            self.canvas.setParent(None)
        plt.close('all')
        fig, axlist = mpf.plot(self.data, type=self.comboType.currentText(), show_nontrading=False, xrotation=20, \
                                datetime_format='%d/%m/%Y', returnfig=True, style = style, volume=self.volume, tight_layout = True)
        self.canvas = FigureCanvasQTAgg(fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layoutEquity.addWidget(self.canvas)
        self.dataMutex.unlock()

    def update_companies(self):
        self.companiesMutex.lock()
        self.listWidgetEquities.clear()
        print(current_thread().name + " Updating companies")
        self.listWidgetEquities.addItems(self.companies)
        self.search_items()
        self.companiesMutex.unlock()

    def search_items(self):
        self.listWidgetEquities.clear()
        for company in self.companies:
            if self.search.text().lower() in company.lower():
                self.listWidgetEquities.addItem(company)

    def start_historical_data(self):
        thread = Thread(target=self.set_data_sync)
        thread.start()

    def set_data_sync(self):
        self.companyMutex.lock()
        print(current_thread().name + " Updating Data")
        data = None
        if self.listWidgetEquities.currentItem() is not None:
            data = self.controller.get_historical(self.listWidgetEquities.currentItem().text(), start = self.dateStart.text(), end = self.dateEnd.text(), interval= self.comboInterval.currentText())
        if data is not None:
            self.data = data
            self.dataSingal.emit()
        else:
            self.messageSignal.emit()
        self.companyMutex.unlock()

    def start_company(self):
        thread = Thread(target=self.set_company_sync)
        thread.start()

    def set_company_sync(self):
        self.companyMutex.lock()
        print(current_thread().name + " Updating Company")
        if self.listWidgetEquities.currentItem() is not None:
            company = self.controller.get_company(self.listWidgetEquities.currentItem().text())
            if company is not None:
                self.company = company
                self.companySignal.emit()
            else:
                self.messageSignal.emit()
        self.companyMutex.unlock()

    def start_companies(self):
        thread = Thread(target=self.set_companies_sync)
        thread.start()

    def set_companies_sync(self):
        self.companiesMutex.lock()
        print(current_thread().name + " Updating Companies")
        result = self.controller.get_index_companies(self.comboIndexes.currentText())
        if result is not None:
            self.companies = result['Name'].tolist()
            self.companiesSignal.emit()
        else:
            self.messageSignal.emit()
        self.companiesMutex.unlock()

    def display_message(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Sorry couldn't get information from server.")
        msg.setWindowTitle("Server Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


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
    app.setStyleSheet(qdarkstyle.load_stylesheet())

    clientView = ClientView()
    clientView.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Exiting')