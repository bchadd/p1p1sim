from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QGridLayout
from PyQt6.QtCore import pyqtSignal
import db
import oracle
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('p1p1sim')
        self.setGeometry(100, 100, 400, 400)
        vbox = QVBoxLayout()

        ## update bulk json
        if not os.path.exists('bulk-data.json'):
            oracle.write_bulk_json()
        else:
            oracle.update_bulk_json()

        ## add button for each .csv in the cubes folder
        self.csvs = [csv for csv in os.listdir('cubes') if csv.endswith('.csv')]
        for csv in self.csvs:
            cube_name = csv[:-4]  ## remove the extension (.csv)
            csv_button = QPushButton(cube_name, self)
            csv_button.clicked.connect(lambda _, cube_name=cube_name: self.button_clicked(cube_name))
            vbox.addWidget(csv_button)

        ## add quit button
        quit_button = QPushButton('Quit', self)
        quit_button.clicked.connect(self.close)
        vbox.addWidget(quit_button)

        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

    def button_clicked(self, cube_name):
        self.pick_window = PickWindow(cube_name=cube_name)
        self.pick_window.pick_completed.connect(self.handle_pick_completed)
        self.hide()
        self.pick_window.show()
    
    def handle_pick_completed(self):
        self.show()

class PickWindow(QWidget):
    pick_completed = pyqtSignal()

    def __init__(self, cube_name):
        super().__init__()
        self.cube_name = cube_name
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f'{self.cube_name} - select p1p1')
        self.setGeometry(500, 100, 400, 400)

        if self.layout():
            layout = self.layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)

        grid = QGridLayout()

        ## establish engine, create tables (if not exist), create cube_list list object
        self.engine = db.create_engine(f'sqlite:///databases//{self.cube_name}.db')
        db.create_tables(self.engine)

        self.list_df = db.create_list_df_from_(self.cube_name)
        db.add_list_to_(self.engine, self.list_df)

        self.cube_list = db.to_list_from_(self.list_df)

        ## create cube card info json
        oracle_uri = oracle.get_oracle_uri()
        oracle.update_oracle_json(oracle_uri)
        filtered_json = oracle.filter_oracle_json_for_(self.cube_list)
        extracted_info_json = oracle.extract_info_from_(filtered_json)

        ## add cube card info to info table
        json_df = db.json_df_from_(extracted_info_json)
        db.add_info_to_(self.engine, json_df)

        ## add 15 buttons in a 3x5 grid
        self.current_pack = db.generate_pack_from_(self.cube_list)
        for index, card in enumerate(self.current_pack):
            button = QPushButton(card)
            button.clicked.connect(lambda _, card=card: self.button_clicked(card))
            grid.addWidget(button, index // 5, index % 5)

        ## add exit button
        exit_button = QPushButton('Exit', self)
        exit_button.clicked.connect(self.handle_exit_button_click)
        grid.addWidget(exit_button, 3, 2, 1, 1)  ## span the button across 5 columns

        self.setLayout(grid)

    def handle_exit_button_click(self):
        self.pick_completed.emit()
        self.close()

    def button_clicked(self, card):
        if card != 'Exit':
            ## pull picked card to the first index position, then add to db
            self.current_pack.insert(0, self.current_pack.pop(self.current_pack.index(card)))
            p1p1 = db.create_picks_object(self.current_pack)
            db.add_pick_to_(self.engine, p1p1)
            
        ## clear widgets from current layout and reload
        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)
        self.init_ui()