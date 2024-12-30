from PyQt5.QtWidgets import QApplication
import sys

from Window.MainWindow import MainWindow
from GlobalVar import GlobalVar

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    #win.show()
    win.show()  # 最大化顯示
    #print(vars(win))
    sys.exit(app.exec_())