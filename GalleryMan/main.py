# Import all the required modules
import argparse
import sys
from PyQt5.QtCore import QPoint, QRect, QSize , Qt
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

class Main:
    def createApp(self):
        app = QApplication([])

        window = QMainWindow()
        
        central = QWidget(window)
        
        layout = QVBoxLayout(central)
        
        scrollArea = QScrollArea(central)
                
        layout.addWidget(scrollArea)
        
        contents = QWidget()
        
        contents.setGeometry(window.geometry())
                
        scrollArea.setWidget(contents)
        
        scrollArea.verticalScrollBar().setEnabled(False)
        
        scrollArea.verticalScrollBar().hide()
        
        scrollArea.horizontalScrollBar().setEnabled(False)
        
        scrollArea.horizontalScrollBar().hide()
    
        layout = QHBoxLayout(contents)
        
        window.setCentralWidget(central)
        
        stylesheet , config = change_with_config(read_file('GalleryMan/sass/styles.txt'))
            
        status = read_file('GalleryMan/galleryman.status')
        
        if(status == 'NOT REGISTERED'):
            ui = FirstPage(contents , window , scrollArea , config)
            
            ui.start()
        else:
            ui = imagesFolder(contents , window , scrollArea , config)
            
            label = QLabel(contents)
            
            label.setMinimumWidth(950)
            
            label.setMinimumHeight(100)
            
            label.move(QPoint(0 , 30))
            
            label.setAlignment(Qt.AlignCenter)
            
            ui.start(label)
                        
        window.setStyleSheet(stylesheet)

        window.show()

        sys.exit(app.exec_())


def main():
    app = Main()
    
    parser = argparse.ArgumentParser(description="A Tool For Managing Your Memories  ")
    
    parser.add_argument("add" , action="store_true" , help="Add A New Directory To the Scanning List")
    
    parser.add_argument("remove" , help="Remove A New Directory To the Scanning List" , action="store_true")

    args = parser.parse_args()
        
    app.createApp()