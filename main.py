import gui
import sys

def main():
    app = gui.QApplication(sys.argv)
    main_window = gui.MainWindow()
    main_window.show()
    app.exec()

if __name__ == '__main__':
    main()