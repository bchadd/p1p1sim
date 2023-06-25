from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QGridLayout
import db
import oracle
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('p1p1sim')
        self.setGeometry(100, 100, 400, 400)
        vbox = QVBoxLayout()

        # Add button for each .csv in the cubes folder
        self.csvs = [csv for csv in os.listdir('cubes') if csv.endswith('.csv')]
        for csv in self.csvs:
            cube_name = csv[:-4]  # Remove the extension (.csv)
            csv_button = QPushButton(cube_name, self)
            csv_button.clicked.connect(self.button_clicked)
            vbox.addWidget(csv_button)

        # Add quit button
        quit_button = QPushButton('Quit', self)
        quit_button.clicked.connect(self.button_clicked)
        vbox.addWidget(quit_button)

        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

    def button_clicked(self):
        sender_button = self.sender()
        button_text = sender_button.text()
        if button_text == 'Quit':
            self.close()
        else:
            oracle.update_oracle_json()
            self.pick_window = PickWindow(cube_name=button_text)
            self.pick_window.show()
            self.hide()  # Hide the main window when pick window is shown

class PickWindow(QWidget):
    def __init__(self, cube_name):
        super().__init__()
        self.cube_name = cube_name
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f'{self.cube_name} - select p1p1')
        self.setGeometry(500, 100, 400, 400)
        grid = QGridLayout()

        self.engine = db.create_engine(f'sqlite:///databases//{self.cube_name}.db')
        db.create_tables(self.engine)
        self.list_df = db.create_list_df_from_(self.cube_name)
        db.add_list_to_(self.engine,self.list_df)

        self.cube_list = db.to_list_from_(self.list_df)

        self.info_json = oracle.filter_json_for_(self.cube_list)
        self.extracted_json = oracle.extract_info_from_(self.info_json)
        db.add_info_to_(self.engine,self.extracted_json)
        
        # Add 15 buttons in a 3x5 grid
        self.current_pack = db.generate_pack_from_(self.cube_list)
        for index, card in enumerate(self.current_pack):
            button = QPushButton(card, self)
            button.clicked.connect(self.button_clicked)
            grid.addWidget(button, index // 5, index % 5)

        # Add exit button
        exit_button = QPushButton('Exit', self)
        exit_button.clicked.connect(self.button_clicked)
        grid.addWidget(exit_button, 3, 2, 1, 1)  # Span the button across 5 columns

        self.setLayout(grid)

    def button_clicked(self):
        sender_button = self.sender()
        button_text = sender_button.text()
        if button_text == 'Exit':
            self.close()
            main_window = MainWindow()
            main_window.show()
        else:
            # Pull picked card to first index position, then add to db
            self.current_pack.insert(0,self.current_pack.pop(self.current_pack.index(button_text)))
            p1p1 = db.create_picks_object(self.current_pack)
            db.add_pick_to_(self.engine,p1p1)
            # Make a new Pick Window instance
            self.close()
            new_pick_window = PickWindow(self.cube_name)
            new_pick_window.show()