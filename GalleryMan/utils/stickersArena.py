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
        self.parent = parent 
        
        self.renderArea = renderArea
        
        self.scrollArea = scrollArea
        
        self.graphics = QGraphicsView(self.parent)
        
        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.graphics.setGeometry(self.parent.geometry())
        
        self.scene = QGraphicsScene()
        
        self.pixmap = self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        self.widget = QWidget()
        
        self.graphics.setScene(self.scene)
        
        self.oldWidget = self.scrollArea.takeWidget()
        
        self.widget.setFixedHeight(100)
        
        self.widget.setFixedWidth(3000)
        
        self.widget.setStyleSheet(self.oldWidget.styleSheet())
        
        self.stickersDict = {}
        
        self.parentlayout = QVBoxLayout()
        
        self.widget.setLayout(self.parentlayout)
        
        self.nameLayout = QHBoxLayout()
        
        self.parentlayout.addLayout(self.nameLayout)
        
        self.preview = QHBoxLayout()
        
        self.parentlayout.addLayout(self.preview)
        
        self.scrollArea.setWidget(self.widget)
        
    def initStock(self):
        for dirs in os.listdir(self.STOCK_PATH):
            parent = self.STOCK_PATH + '/' + dirs
            
            if(not os.path.isdir(parent) or dirs == "Beard"): continue
            
            # name = QLabel()
            
            # name.setText(dirs)
            
            # name.setFixedSize(50 , 50)
            
            # self.nameLayout.addWidget(name)
            
            for stickers in os.listdir(parent):
                preview = CustomLabel()
                
                preview.setFixedSize(50 , 50)
                
                preview.setScaledContents(True)
                
                preview.setPixmap(QPixmap(parent + '/' + stickers).scaled(50 , 50 , transformMode=Qt.SmoothTransformation))
                
                preview.clicked.connect(functools.partial(self.useSticker , parent + '/' + stickers))
                
                preview.setCursor(QCursor(Qt.PointingHandCursor))

                self.preview.addWidget(preview)
                
            break
        
    def useSticker(self , name , event):
        preview = QGripLabel(None , False)
        
        preview.setGeometry(500 , 500 , 300 , 300)
        
        preview.setPixmap(QPixmap(name))
        
        preview.setScaledContents(True)
        
        inst = self.scene.addWidget(preview)
        
        center = inst.boundingRect().center()
        
        t = QTransform()
        
        t.translate(center.x() , center.y())
        
        t.rotate(75)
        
        t.translate(-center.x() , -center.y())
        
        inst.setTransform(t)
        
        self.graphics.show()