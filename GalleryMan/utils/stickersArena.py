from PIL import Image
from PyQt5.QtCore import QPoint, QPointF, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QKeySequence, QMouseEvent, QPixmap, QTransform
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QShortcut, QSizePolicy, QVBoxLayout, QWidget
import functools
import os
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
    STOCK_PATH = os.path.join(os.path.expanduser("~") , ".galleryman" , "stickers")
    
    def __init__(self , parent , renderArea , scrollArea: QScrollArea):
        # Make args global
        self.parent = parent 
        
        self.renderArea = renderArea
        
        self.scrollArea = scrollArea
        
        self.grandparentsLayout = QHBoxLayout()
        
        
        # QGraphics and QScene
        self.graphics = QGraphicsView(parent)

        self.graphics.move(QPoint(0 , 0))
        
        self.graphics.setFixedSize(parent.size())
        
        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scene = QGraphicsScene()
        
        self.graphics.setScene(self.scene)
        
        self.pixmap = self.scene.addPixmap(QPixmap(os.path.join("GalleryMan" , "assets" , "processed_image.png")))
        
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
        
        self.shortcut.activated.connect(self.attachSticker)
        
        # Parent layout to store both the name and the stickers preview
        self.parentlayout = QVBoxLayout()
        
        self.grandparentsLayout.addLayout(self.parentlayout)
        
        self.nameLayout = QHBoxLayout()
        
        self.parentlayout.addLayout(self.nameLayout)
        
        self.cross = QCustomButton("X" , None).create()
        
        self.cross.setBaseSize(50 , 50)
        
        self.grandparentsLayout.addWidget(self.cross)
        
        self.widget.setLayout(self.grandparentsLayout)
        
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
            
        self.switchTo(dirs)
                        
    def useSticker(self , name , event):
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
            "Rotation": 0
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
            oldWidget = self.scrollArea.takeWidget()
            
            parent = QWidget()
            
            parent.setStyleSheet(oldWidget.styleSheet())
            
            parent.setGeometry(oldWidget.geometry())
            
            grandLayout = QHBoxLayout()
                                    
            self.cross.setParent(None)
            
            self.cross.setFixedSize(50 , 50)
            
            self.cross.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            
            grandLayout.addWidget(self.cross)
            
            layout = QVBoxLayout()
            
            self.nameLayout.setParent(None)
            
            layout.addLayout(self.nameLayout)
            
            layout.addLayout(self.stickersDict[name])
                    
            parent.setFixedWidth(self.stickersDict[name].count() * 130)
                        
            grandLayout.addLayout(layout)
            
            layout.setParent(None)
                
            parent.setLayout(grandLayout)
        
            self.scrollArea.setWidget(parent)
            
            self.animation = Animation.fadingAnimation(Animation , self.scrollArea.parent() , 200 , True)
            
            self.animation.start()
            
        self.animation = Animation.fadingAnimation(Animation , self.scrollArea.parent() , 200)
        
        self.animation.finished.connect(run_second)
        
        self.animation.start()
        
    def attachSticker(self):
        self.menu.hide()
        
        before = Image.open(os.path.join("GalleryMan" , "assets" , "processed_image.png"))
        
        sticker = Image.open(self.currentlyUsing)
        
        try:
            before.paste(sticker , (50 , 50 , 700 , 700))
        except Exception as e:
            pass
            
        before.save(os.path.join("GalleryMan" , "assets" , "processed_image.png"))
        
        before.show()