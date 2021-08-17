# # Import all the required modules
from .utils.stickerManager import stickerManager
from .utils.helpers import addToScanDirectory, removeFromScanDirectory, show_list
from .utils.initer import Initer, bcolors
from functools import partial
import argparse , json , os , sys
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QCursor, QKeyEvent, QMouseEvent
from .views.firstPage import FirstPage
from .utils.readers import read_file , change_with_config
from .views.folderview import imagesFolder
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel , QMainWindow, QPushButton, QScrollArea, QVBoxLayout, QWidget
from .assets.singleFolder import singleFolderView
    
class CustomLabel(QLabel):
    clicked = pyqtSignal(QMouseEvent)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.clicked.emit(event)

                      
class Main:
    def createApp(self , showOnlyImage=False , directory=None):
        # A Variable which will handle the current window
        self.curr = "Hide"
        
        # Create a application and a window
        app = QApplication([])
        
        self.window = QMainWindow()
        
        self.window.emergenceSituation = pyqtSignal()
        
        self.window.closeEvent = self.cleanClose
        
        # Set window title
        self.window.setWindowTitle("GalleryMan")
        
        # Mouse events
        self.window.mousePressEvent = self.mouseHandler
        
        self.window.keyPressEvent = self.keyHandler
        
        # Prevent exiting of the program when a error breaks
        def except_hook(cls, exception, traceback):
            # sys.__excepthook__(cls, exception, traceback)
           raise AttributeError(exception).with_traceback(traceback)
            
        # Use a custom function to handle errors
        sys.excepthook = except_hook
        
        # Create central widget and layout
        central = QWidget(self.window)
        
        layout = QVBoxLayout(central)
        
        # Main window should be a scrollable
        self.scrollArea = QScrollArea(central)
        
        # Add to screen
        layout.addWidget(self.scrollArea)
        
        # A Widget where the contents will be rendered
        contents = QWidget(self.window)
        
        # Adjustments
        contents.setGeometry(self.window.geometry())
                
        self.scrollArea.setWidget(contents)
        
        
        self.scrollArea.verticalScrollBar().setEnabled(False)
        
        self.scrollArea.verticalScrollBar().hide()
        
        self.scrollArea.horizontalScrollBar().setEnabled(False)
        
        self.scrollArea.horizontalScrollBar().hide()
        
        layout = QHBoxLayout(contents)
        
        # Add a topbar to the window
        self.helper = CustomLabel(self.window)
        
        self.helper.clicked.connect(self.show_hides)
        
        
        # Stylings and ajustments
        self.helper.setGeometry(QRect(
            0 , 0,
            1980,
            50
        ))
        
        self.helper.show()
        
        # Create a topbar
        self.topbar = QLabel(self.window)
        
        self.topbar.setGeometry(QRect(
            self.window.width() - 400 , 0,
            200,
            50
        ))
        
        self.topbar.setStyleSheet("background-color: transparent")
        
        self.topbar.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        self.helper.setStyleSheet('background-color: transparent;')
        
        # Create a lyout and add all the widgets 
        layoout = QHBoxLayout()
        
        j = 0
        
        functions = [
            lambda : self.window.showMinimized(),
            lambda : self.window.showFullScreen(),
            lambda : app.exit(1)
        ]
        
        # stylesheet , config = change_with_config(read_file('GalleryMan/sass/styles.txt'))
        
        stylesheet , config = change_with_config(read_file(os.path.join("GalleryMan" , "sass" , "styles.txt")))
        
        # Iterate through all the user's preferred icons
        for icon , color , size , font in json.loads(config.get("global" , "topBar-buttons")):            
            button = QPushButton(icon , self.topbar)
            
            button.setCursor(QCursor(Qt.PointingHandCursor))
            
            button.clicked.connect(functions[j])
            
            button.setFlat(True)
            
            button.setStyleSheet('font-family: {}; color: {}; font-size: {}px'.format(
                font , color , size
            ))
            
            layoout.addWidget(button , alignment=Qt.AlignTop | Qt.AlignRight)
        
        # Print some thanks when the user presses the exit key (as the last key is indeed the cross key)
        button.clicked.connect(lambda : print("Thanks for using GalleryMan!"))
        
        button.clicked.connect(exit)
            
        self.topbar.setLayout(layoout)
                
        self.window.setCentralWidget(central)
        
        # Read status
        status = read_file(os.path.join("GalleryMan" , "galleryman.status"))
                
        label = QLabel(contents)
            
        label.setMinimumWidth(950)
        
        label.setMinimumHeight(100)
        
        label.move(QPoint(0 , 30))
        
        label.setAlignment(Qt.AlignCenter)
        
        if(showOnlyImage):
            ui = singleFolderView()
            
            ui.init(self.window , None , config , self.scrollArea , self.window , app , self.topbar  , self.helper , label)
            
            self.window.show()
            
            self.helper.show()
            
            ui.show_image(directory , None , True)
            
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
           
        with open(os.path.join(os.path.expanduser("~") , ".config" , "galleryman" , "data" , "scan_dirs.txt") , "w") as f:
            f.write("[]")
        
        
    def mouseHandler(self , _):
        try:
            self.button.hide()
            
        except:
            pass
        
    def messageHandler(self , msg_type , msg_log_content , msg_string):
        pass
    
    def cleanClose(self , event: QCloseEvent):
        return QMainWindow.closeEvent(self.window , event)
        
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
    
    # Handle args
    if(args.init):
        Initer().init()
        
    elif(args.show):
        directory = os.path.abspath(args.show)
        
        if(os.path.isfile(directory)):        
            app.createApp(True , directory)
        else:
            print(bcolors.FAIL + "The path provided is not correct. Please check it again. \nExiting...")
    
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