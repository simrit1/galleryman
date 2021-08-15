# Import all the required modules
from GalleryMan.utils.stickerManager import stickerManager
from GalleryMan.utils.helpers import addToScanDirectory, removeFromScanDirectory, show_list
from GalleryMan.utils.initer import Initer
from functools import partial
from GalleryMan.assets.QtHelpers import QCustomButton
import argparse
import json
from os import system
import os
import sys
from PyQt5.QtCore import QPoint, QRect, QSize , Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QKeyEvent, QMouseEvent
from GalleryMan.views.firstPage import FirstPage
from GalleryMan.utils.readers import read_file , change_with_config
from GalleryMan.views.folderview import imagesFolder
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel , QMainWindow, QPushButton, QScrollArea, QVBoxLayout, QWidget
from GalleryMan.assets.singleFolder import singleFolderView

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
    def createApp(self , showOnlyImage=False , directory=None):
        self.curr = "Hide"
        
        app = QApplication([])
                
        self.window = QMainWindow()
        
        self.window.setWindowTitle("GalleryMan")
        
        self.window.mousePressEvent = self.mouseHandler
        
        self.window.keyPressEvent = self.keyHandler
                
        def except_hook(cls, exception, traceback):
            sys.__excepthook__(cls, exception, traceback)
            
        sys.excepthook = except_hook
        
        central = QWidget(self.window)
        
        layout = QVBoxLayout(central)
        
        self.scrollArea = QScrollArea(central)
                        
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
        
        self.topbar = QLabel(self.window)
        
        self.topbar.setGeometry(QRect(
            self.window.width() - 400 , 0,
            200,
            50
        ))
        
        self.topbar.setStyleSheet("background-color: transparent")
        
        self.topbar.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        self.helper.setStyleSheet('background-color: transparent;')
        
        layoout = QHBoxLayout()
        
        j = 0
        
        functions = [
            lambda : self.window.showMinimized(),
            lambda : self.window.showFullScreen(),
            lambda : app.exit(1)
        ]
        
        stylesheet , config = change_with_config(read_file('GalleryMan/sass/styles.txt'))
        
        for icon , color , size , font in json.loads(config.get("global" , "topBar-buttons")):            
            button = QPushButton(icon , self.topbar)
            
            button.setCursor(QCursor(Qt.PointingHandCursor))
            
            button.clicked.connect(functions[j])
            
            button.setFlat(True)
            
            button.setStyleSheet('font-family: {}; color: {}; font-size: {}px'.format(
                font , color , size
            ))
            
            layoout.addWidget(button , alignment=Qt.AlignTop | Qt.AlignRight)
            
        button.clicked.connect(lambda : print("Thanks for using GalleryMan!"))
        
        button.clicked.connect(exit)
            
        self.topbar.setLayout(layoout)
                
        self.window.setCentralWidget(central)
            
        status = read_file('GalleryMan/galleryman.status')
                
        label = QLabel(contents)
            
        label.setMinimumWidth(950)
        
        label.setMinimumHeight(100)
        
        label.move(QPoint(0 , 30))
        
        label.setAlignment(Qt.AlignCenter)
        
        if(showOnlyImage):
            ui = singleFolderView()
            
            ui.init(self.window , None , config , self.scrollArea , self.window , app , label)
            
            self.window.show()
            
            self.topbar.show()
            
            ui.show_image(directory , None)
            
        elif(status == 'NOT REGISTERED'):            
            ui = FirstPage(contents , self.window , self.scrollArea , config , self.topbar , app)
                        
            ui.start()
            
        else:
            ui = imagesFolder(contents , self.window , self.scrollArea , config , self.topbar , app)        
        
            ui.start(label)
        
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
        if(event.key() == Qt.Key_F11):
            if(self.window.isFullScreen()):
                self.window.showNormal()
            else:
                self.window.showFullScreen()
                
    def create_files(self):    
        with open("/home/strawhat54/.config/galleryman/data/scan_dirs.txt" , "w") as f:
            f.write("[]")
        
        
    def mouseHandler(self , _):
        try:
            self.button.hide()
            
        except:
            pass
        
    def messageHandler(self , msg_type , msg_log_content , msg_string):
        pass
        
def main():
    app = Main()
    
    parser = argparse.ArgumentParser(description="A Tool For Managing Your Memories  ")
    
    parser.add_argument("--list" , dest="list" , action="store_true" , help="Show all the directories that are prevent to be scanned")
    
    parser.add_argument("--add" , dest="add" , action="store_true" , help="Add A New Directory To the Scanning List")
    
    parser.add_argument("--remove" , dest="remove" , help="Remove A New Directory To the Scanning List" , action="store_true")
                
    parser.add_argument("--init" , dest="init" , help="Initiates GalleryMan" , action="store_true")
    
    parser.add_argument("--stickers" , dest="stickers" , help="Shows a list of all the stickers downloaded" , action="store_true")
    
    parser.add_argument("--create" , dest="create" , help="Creates a new sticker pack to be used in application" , action="store_true")
    
    parser.add_argument("--install" , dest="install" , help="Add an image to a sticker pack")
    
    parser.add_argument("--delete" , dest="delete" , help="Deletes a sticker pack" , action="store_true")
    
    parser.add_argument("--show" , dest="show" , help="Shows a particular image")

    args = parser.parse_args()
    
    try:
        os.remove("~/.galleryman/currentlyOpened.png")
    except:
        pass
    
    if(args.init):
        Initer().init()
        
    elif(args.show):
        directory = os.getcwd()
        
        directory = os.path.join(directory , args.show)
        
        app.createApp(True , directory)
    
    elif(args.list):
        show_list()
    
    elif(args.add):
        addToScanDirectory(args.add)
        
    elif(args.remove):
        removeFromScanDirectory(args.remove)    
        
    elif(args.create):
        stickerManager().createNew()
        
    elif(args.install):
        stickerManager().addToExisting(args.install)
    
    elif(args.delete):
        stickerManager().deletePack()
    
    else:
        app.createApp()