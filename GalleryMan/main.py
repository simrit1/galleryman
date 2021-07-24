# Import all the required modules
from functools import partial
from GalleryMan.assets.QtHelpers import QCustomButton
import argparse
from os import system
import os
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QEvent, QObject, QPoint, QRect, QSize, QThread , Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QKeyEvent, QMouseEvent
from GalleryMan.views.firstPage import FirstPage
from GalleryMan.utils.readers import read_file , change_with_config
from GalleryMan.views.folderview import imagesFolder
from PyQt5.QtWidgets import QApplication, QGraphicsOpacityEffect, QHBoxLayout, QLabel , QMainWindow, QPushButton, QScrollArea, QVBoxLayout, QWidget

class ScrollLabel(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
 
        self.setWidgetResizable(True)
 
        content = QWidget(self)
        
        self.setWidget(content)
 
        lay = QVBoxLayout(content)
 
        self.label = QLabel(content)
 
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
 
        self.label.setWordWrap(True)
 
        lay.addWidget(self.label)

    
class CustomLabel(QLabel):
    clicked = pyqtSignal(QMouseEvent)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.clicked.emit(event)

                      
class Main:
    def createApp(self):
        self.curr = "Hide"
        
        app = QApplication([])
                
        self.window = QMainWindow()
        
        self.window.mousePressEvent = self.mouseHandler
        
        self.window.keyPressEvent = self.keyHandler
        
        central = QWidget(self.window)
        
        layout = QVBoxLayout(central)
        
        self.scrollArea = QScrollArea(central)
        
        self.scrollArea.verticalScrollBar().valueChanged.connect(self.valueHandler)
                
        layout.addWidget(self.scrollArea)
        
        contents = QWidget(self.window)
        
        contents.setGeometry(self.window.geometry())
                
        self.scrollArea.setWidget(contents)
        
        self.scrollArea.verticalScrollBar().setEnabled(False)
        
        self.scrollArea.verticalScrollBar().hide()
        
        self.scrollArea.horizontalScrollBar().setEnabled(False)
        
        self.scrollArea.horizontalScrollBar().hide()
    
        layout = QHBoxLayout(contents)
        
        self.helper = CustomLabel(self.window)
        
        self.helper.clicked.connect(self.show_hides)
        
        self.helper.setGeometry(QRect(
            0 , 0,
            1980,
            50
        ))
        
        self.helper.show()
        
        self.topbar = QLabel(self.helper)
        
        self.topbar.setGeometry(QRect(
            1600 , 0,
            200,
            50
        ))
        
        self.topbar.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        self.topbar.setStyleSheet('background-color: transparent;')
        
        layoout = QHBoxLayout()
        
        j = 0
        
        functions = [
            self.window.showMinimized,
            self.window.showMaximized,
            app.quit
        ]
        
        for i in [" " , "  " , "  "]:            
            button = QPushButton(i , self.topbar)
            
            button.setCursor(QCursor(Qt.PointingHandCursor))
            
            button.clicked.connect(functions[j])
            
            button.setFlat(True)
            
            button.setStyleSheet('font-family: "SauceCodePro Nerd Font"; color: #88C0D0; font-size: 25px')
            
            layoout.addWidget(button , alignment=Qt.AlignTop | Qt.AlignRight)
            
        self.topbar.setLayout(layoout)
                
        self.window.setCentralWidget(central)
        
        stylesheet , config = change_with_config(read_file('GalleryMan/sass/styles.txt'))
            
        status = read_file('GalleryMan/galleryman.status')
                
        label = QLabel(contents)
            
        label.setMinimumWidth(950)
        
        label.setMinimumHeight(100)
        
        label.move(QPoint(0 , 30))
        
        label.setAlignment(Qt.AlignCenter)

        if(status == 'NOT REGISTERED'):            
            ui = FirstPage(contents , self.window , self.scrollArea , config)
            
            args = []
        else:
            ui = imagesFolder(contents , self.window , self.scrollArea , config)
            
            args = [label]
        
        ui.start(*args)
        
        self.window.setStyleSheet(stylesheet)

        sys.exit(app.exec_())
    
    def hide(self):
        self.button.hide()
        
        self.helper.hide()
        
    def show_hides(self , event: QMouseEvent):
        try:
            self.button.hide()
        except:
            pass
        
        self.button = QPushButton(self.curr , self.window)
        
        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        
        self.button.setFlat(True)
        
        self.button.setStyleSheet("border: 1px solid #3B4252; font-size: 30px; font-family: Comfortaa")
        
        self.button.move(event.pos())
        
        self.button.setFixedSize(QSize(200 , 50))
                
        if(self.curr == "Hide"):
            
            self.button.clicked.connect(self.topbar.hide)
            
            self.button.clicked.connect(self.button.hide)
                        
            self.button.clicked.connect(partial(self.update , "Show"))
        else:            
            self.button.clicked.connect(self.topbar.show)
            
            self.button.clicked.connect(self.button.hide)
            
            self.button.clicked.connect(partial(self.update , "Hide"))
        
        self.button.show()
        
    def update(self , new):
        self.curr = new
        
    def keyHandler(self , event: QKeyEvent):
        if(event.key() == QtCore.Qt.Key_F11):
            if(self.window.isFullScreen()):
                self.window.showNormal()
            else:
                self.window.showFullScreen()
                
    def create_files(self):    
        with open("/home/strawhat54/.config/galleryman/data/scan_dirs.txt" , "w") as f:
            f.write("[]")
            
    def valueHandler(self):
        value = self.scrollArea.verticalScrollBar().value()
                
        if(value == 0):
            stylesheet = "background-color: rgb(46 , 52 , 64)"
        
        else:
            stylesheet = "background-color: rgba(46 , 52 , 64 , 75)"
            
        self.helper.setStyleSheet(stylesheet)
        
    def mouseHandler(self , _):
        try:
            self.button.hide()
            
        except:
            pass
        
def main():
    app = Main()
    
    parser = argparse.ArgumentParser(description="A Tool For Managing Your Memories  ")
    
    parser.add_argument("--add" , dest="add" , action="store_true" , help="Add A New Directory To the Scanning List")
    
    parser.add_argument("--remove" , dest="remove" , help="Remove A New Directory To the Scanning List" , action="store_true")
    
    parser.add_argument("--backup" , dest="remove" , help="Creates a backup of your data and config in current directory ({})".format(os.getcwd()) , action="store_true")
    
    parser.add_argument("--restore" , dest="remove" , help="Restores a created backup" , action="store_true")
    
    parser.add_argument("--reset" , dest="remove" , help="Resets all configs and data" , action="store_true")
    
    parser.add_argument("--open" , dest="open" , help="Opens config file" , action="store_true")

    args = parser.parse_args()
    
    if(args.add):
        input("Enter the file location (Press enter to select cwd): ")
    elif(args.open):
        system("nano config.ini || emacs config.ini || vim config.ini || code config.ini || echo 'Oops! You dont have a preferred editor!'")
    else:
        app.createApp()