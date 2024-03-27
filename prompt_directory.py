from PyQt5.QtWidgets import QApplication, QFileDialog
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(QFileDialog.getExistingDirectory())
