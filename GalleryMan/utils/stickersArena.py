from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QMouseEvent, QPixmap, QTransform
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView, QHBoxLayout, QLabel, QVBoxLayout, QWidget
import functools
import os
from GalleryMan.utils.helpers import QGripLabel

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
    STOCK_PATH = "/home/strawhat54/.galleryman/stickers"
    
    def __init__(self , parent , renderArea , scrollArea):
        
        # Make args global
        self.parent = parent 
        
        self.renderArea = renderArea
        
        self.scrollArea = scrollArea
        
        # QGraphics and QScene
        self.graphics = QGraphicsView(self.parent)
        
        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.graphics.setGeometry(self.parent.geometry())
        
        self.scene = QGraphicsScene()
        
        self.pixmap = self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
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
        
        self.stickersDict = {}
        
        # Parent layout to store both the name and the stickers preview
        self.parentlayout = QVBoxLayout()
        
        self.widget.setLayout(self.parentlayout)
        
        self.nameLayout = QHBoxLayout()
        
        self.parentlayout.addLayout(self.nameLayout)
        
        self.preview = QHBoxLayout()
        
        self.parentlayout.addLayout(self.preview)
        
        self.scrollArea.setWidget(self.widget)
        
    def initStock(self):
        
        # Iterate through all the folders in the folders path
        for dirs in os.listdir(self.STOCK_PATH):
            
            # Get the parent
            parent = self.STOCK_PATH + '/' + dirs
            
            # Check if it is a directory
            if(not os.path.isdir(parent)): continue
            
            
            # Add a label to the name's layout
            name = QLabel()
            
            name.setText(dirs)
            
            name.setFixedSize(50 , 50)
            
            self.nameLayout.addWidget(name)
            
            # Iterate through all the stickers in the folder
            for stickers in os.listdir(parent):
                
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
                
            break
        
    def useSticker(self , name , event):
        # Create a grip label
        preview = QGripLabel(None , False)
        
        # Set geometry
        preview.setGeometry(500 , 500 , 300 , 300)
        
        # Set pixmap
        preview.setPixmap(QPixmap(name))
        
        # Scaled contents
        preview.setScaledContents(True)
        
        # Add to the scene
        inst = self.scene.addWidget(preview)
        
        # Get the center of the widget
        center = inst.boundingRect().center()
        
        t = QTransform()
        
        t.translate(center.x() , center.y())
        
        t.rotate(75)
        
        t.translate(-center.x() , -center.y())
        
        inst.setTransform(t)
        
        self.graphics.show()