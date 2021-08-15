
from PyQt5.QtCore import QPoint, QRect, QSize, QSizeF, Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QKeySequence, QMouseEvent, QPixmap, QTransform
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsProxyWidget, QGraphicsScene, QGraphicsView, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QShortcut, QSystemTrayIcon, QVBoxLayout, QWidget
import functools
import os
from GalleryMan.utils.helpers import QGripLabel
from GalleryMan.assets.QtHelpers import Animation, QCustomButton, QSliderMenu

class CustomLabel(QLabel):
    clicked = pyqtSignal(QPoint)

    def __init__(self, parent=None, listenFor=Qt.LeftButton):
        super().__init__(parent=parent)

        self.listenFor = listenFor

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == self.listenFor:
            self.clicked.emit(event.pos())

            self.eventPos = event.pos()


class stickersViewer:
    STOCK_PATH = "/home/strawhat54/.galleryman/stickers/"
    
    def __init__(self , parent , renderArea , scrollArea: QScrollArea):
        # Make args global
        self.parent = parent 
        
        self.renderArea = renderArea
        
        self.scrollArea = scrollArea
        
        # QGraphics and QScene
        self.graphics = QGraphicsView(self.parent)
        
        self.graphics.setGeometry(self.parent.geometry())
        
        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scene = QGraphicsScene()
        
        self.pixmap = self.scene.addPixmap(QPixmap("./GalleryMan/assets/processed_image.png"))
        
        self.graphics.setScene(self.scene)
        
        # Scroll Widget
        self.widget = QWidget()
        
        # Take the old widget
        self.oldWidget = self.scrollArea.takeWidget()
        
        # Set new sizes 
        self.widget.setFixedHeight(100)
        
        self.widget.setFixedWidth(3000)
        
        # Stylings
        self.widget.setStyleSheet(self.oldWidget.styleSheet())
        
        self.stickersDict: list[QVBoxLayout] = {}
        
        self.shortcut = QShortcut(QKeySequence("Ctrl+S") , self.graphics)
        
        # self.shortcut.activated.connect(self.attachSticker)
        
        # Parent layout to store both the name and the stickers preview
        self.parentlayout = QVBoxLayout()
        
        self.widget.setLayout(self.parentlayout)
        
        self.nameLayout = QHBoxLayout()
        
        self.parentlayout.addLayout(self.nameLayout)
        
        self.scrollArea.setWidget(self.widget)
        
    def initStock(self):
        directories = os.listdir(self.STOCK_PATH)
        
        # Iterate through all the folders in the folders path
        for dirs in directories:
            
            self.preview = QHBoxLayout()
            
            # Get the parent
            parent = self.STOCK_PATH + '/' + dirs
            
            # Check if it is a directory
            if(not os.path.isdir(parent)): continue
            
            # Add a label to the name's layout
            name = QCustomButton(dirs , None).create()
                        
            name.setStyleSheet("""
                font-size: Comfortaa;
                font-size: 20px;                   
            """)
            
            name.clicked.connect(functools.partial(self.switchTo , dirs))
            
            self.nameLayout.addWidget(name)
            
            sticker = os.listdir(parent)
            
            self.widget.setFixedWidth(len(sticker) * 100)
            
            # Iterate through all the stickers in the folder
            for stickers in sticker:
                
                # Create a clickable label
                preview = CustomLabel()
                
                
                # Set fixed size
                preview.setFixedSize(50 , 50)
                
                # Scaled contents
                preview.setScaledContents(True)
                
                # Set the image
                preview.setPixmap(QPixmap(parent + '/' + stickers).scaled(50 , 50 , transformMode=Qt.SmoothTransformation))
                
                # Call the function which will handle the usage of the sticker on click
                preview.clicked.connect(functools.partial(self.useSticker , parent + '/' + stickers))
                
                # Set the cursor
                preview.setCursor(QCursor(Qt.PointingHandCursor))
                
                # Add the widget to the preview
                self.preview.addWidget(preview)
                
            self.stickersDict[dirs] = self.preview
            
        self.switchTo("Emoji")
                        
    def useSticker(self , name , event):
        # # Create a grip label
        # self.preview = QLabel()
        
        # # Set geometry
        # self.preview.setGeometry(500 , 500 , 300 , 300)
        
        # self.preview.setStyleSheet("""background-color: transparent""")
        
        # # Set pixmap
        # self.preview.setPixmap(QPixmap(name))
        
        # # Scaled contents
        # self.preview.setScaledContents(True)
        
        # self.sticker = self.scene.addWidget(self.preview)
        self.currentlyUsing = name
        
        self.sticker = self.scene.addPixmap(QPixmap(name))
    
        self.sticker.setPos(QPoint(75 , 75))    
        
        self.sticker.setFlag(QGraphicsItem.ItemIsMovable)
        
        self.menu = QSliderMenu(self.graphics)
        
        crossLabel = QVBoxLayout()
        
        cross = QLabel()
        
        cross.setFixedSize(QSize(50 , 50))
        
        cross.setText("X")
        
        self.config = {
            "Width": 300,
            "Height":300,
            "rotation": 0
        }
        
        crossLabel.addWidget(cross , alignment=Qt.AlignTop | Qt.AlignLeft)
        
        self.menu.addMenu("" , crossLabel , True)
        
        for name in ["Width" , "Height" , "Rotation"]:
            inputBox = QLineEdit()
            
            inputBox.setPlaceholderText(name)
            
            inputBox.setStyleSheet("""
                color: #D8DEE9;
                padding-left: 20px;    
            """)
            
            inputBox.setFixedHeight(50)
            
            inputBox.textChanged.connect(functools.partial(self.update , inputBox , name))
            
            self.menu.addMenu(name , inputBox)
            
        self.menu.move(QPoint(2000 , 0))
        
        self.menu.show()
        
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1877 - self.menu.width(), 0) , 200)
        
        self.animation.start()
        
        self.graphics.show()
        
    def update(self , inputBox , name):
        text = int(inputBox.text())
        
        self.config[name] = text
        
        self.scene.removeItem(self.sticker)
        
        self.sticker.hide()
        
        pos = self.sticker.pos()
        
        self.sticker = self.scene.addPixmap(QPixmap(self.currentlyUsing).scaled(self.config["Width"] , self.config["Height"] , transformMode=Qt.SmoothTransformation))
        
        self.sticker.setPos(pos)
        
        self.sticker.setFlag(QGraphicsItem.ItemIsMovable)
        
        self.sticker.show()
        
        self.sticker.setTransformOriginPoint(self.sticker.boundingRect().center())
        
        self.sticker.setTransform(QTransform().rotate(self.config["Rotation"]))
        
    def switchTo(self , name):
        def run_second():        
            widget = QWidget()
            
            oldWidget = self.scrollArea.takeWidget()
            
            widget.setStyleSheet(oldWidget.styleSheet())
            
            widget.setGeometry(oldWidget.geometry())
            
            layout = QVBoxLayout()
            
            self.nameLayout.setParent(None)
            
            layout.addLayout(self.nameLayout)
            
            layout.addLayout(self.stickersDict[name])
            
            widget.setFixedWidth(self.stickersDict[name].count() * 130)
                
            widget.setLayout(layout)
        
            self.scrollArea.setWidget(widget)
            
            self.animation = Animation.fadingAnimation(Animation , self.scrollArea.parent() , 200 , True)
            
            self.animation.start()
            
        self.animation = Animation.fadingAnimation(Animation , self.scrollArea.parent() , 200)
        
        self.animation.finished.connect(run_second)
        
        self.animation.start()