# Import all the required modules
import argparse
from os import system
import os
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QPoint, QRect, QSize, QThread , Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from GalleryMan.views.firstPage import FirstPage
from GalleryMan.utils.readers import read_file , change_with_config
from GalleryMan.views.folderview import imagesFolder
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel , QMainWindow, QScrollArea, QVBoxLayout, QWidget

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
        
class Worker(QObject):
    finished = pyqtSignal()

    def run(self , parent , status , scrollArea , config , contents , label):
        
            
        self.finished.emit()
                                
class Main:
    def createApp(self):
        app = QApplication([])

        self.window = QMainWindow()
        
        self.window.keyPressEvent = self.keyHandler
        
        central = QWidget(self.window)
        
        layout = QVBoxLayout(central)
        
        scrollArea = QScrollArea(central)
                
        layout.addWidget(scrollArea)
        
        contents = QWidget(self.window)
        
        contents.setGeometry(self.window.geometry())
                
        scrollArea.setWidget(contents)
        
        scrollArea.verticalScrollBar().setEnabled(False)
        
        scrollArea.verticalScrollBar().hide()
        
        scrollArea.horizontalScrollBar().setEnabled(False)
        
        scrollArea.horizontalScrollBar().hide()
    
        layout = QHBoxLayout(contents)
        
        self.window.setCentralWidget(central)
        
        stylesheet , config = change_with_config(read_file('GalleryMan/sass/styles.txt'))
            
        status = read_file('GalleryMan/galleryman.status')
                
        label = QLabel(contents)
            
        label.setMinimumWidth(950)
        
        label.setMinimumHeight(100)
        
        label.move(QPoint(0 , 30))
        
        label.setAlignment(Qt.AlignCenter)

        if(status == 'NOT REGISTERED'):            
            ui = FirstPage(contents , self.window , scrollArea , config)
            
            ui.start()
        else:
            ui = imagesFolder(contents , self.window , scrollArea , config)
            
            ui.start(label)
        
        self.window.setStyleSheet(stylesheet)

        sys.exit(app.exec_())
        
    def keyHandler(self , event: QKeyEvent):
        if(event.key() == QtCore.Qt.Key_F11):
            if(self.window.isFullScreen()):
                self.window.showNormal()
            else:
                self.window.showFullScreen()
                
    def create_files(self):    
        with open("/home/strawhat54/.config/galleryman/data/scan_dirs.txt" , "w") as f:
            f.write("[]")
            


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