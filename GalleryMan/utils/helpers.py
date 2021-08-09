# Importing the modules
from math import cos, radians, sin
from PyQt5.QtCore import  QPoint, QRect, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPainter , QResizeEvent
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRubberBand,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
)
from json import loads, dumps

# A Custom, Draggable label
class DraggableLabel(QLabel):
    moved = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)

        self.setStyleSheet("background: transparent;")

        self.origin = None

    def setLimits(self, rect):
        self.limits = rect
        
    # Listen for mouse events
    def mousePressEvent(self, event):
        if not self.origin:
            self.origin = self.pos()
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.mousePos)

            self.moved.emit()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.limits.contains(self.geometry()):
                self.move(self.origin)

# A Draggable input
class DraggableInput(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("background: transparent;")
        self.origin = None

    def setLimits(self, rect):
        self.limits = rect

    # Mouse listens
    def mousePressEvent(self, event):
        if not self.origin:
            self.origin = self.pos()
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.mousePos)

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.LeftButton:
                if not self.limits.contains(self.geometry()):
                    self.move(self.origin)
        except:
            pass


# Class for ading to like
class AddToLiked:
    def __init__(self, parent, dir, remove=False):
        self.dir = dir

        self.remove = remove

    def run(self):
        with open("/home/strawhat54/.galleryman/data/likedFolders.txt", "r") as f:
            data = f.read()
        

            if data == "":
                data = []

            else:
                data = loads(data)
        data = []

        with open("/home/strawhat54/.galleryman/data/likedFolders.txt", "w") as f:
            if self.remove:
                data.remove(self.dir)

            else:
                data.append(self.dir)

            f.write(dumps(data))


class ResizableRubberBand(QWidget):
    def __init__(self, parent=None):
        
        super(ResizableRubberBand, self).__init__(parent)
            
        self.mousePressPos = None
        
        self.mouseMovePos = None
        
        self.origin = None
        
        self.borderRadius = 0

        self.setWindowFlags(Qt.SubWindow)
        
        layout = QHBoxLayout(self)
        
        layout.setContentsMargins(0, 0, 0, 0)
            
        layout.addWidget(
            QSizeGrip(self), 0,
            Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(
            QSizeGrip(self), 0,
            Qt.AlignRight | Qt.AlignBottom)
        
        self._band = QRubberBand(
            QRubberBand.Rectangle, self)
        
        self.setStyleSheet('background-color: #2E344050')
                        
        self._band.show()
        
    def resizeEvent(self, event):
        self._band.resize(self.size())

    def paintEvent(self, event):
        window_size = self.size()

        qp = QPainter()

        qp.begin(self)

        qp.setRenderHint(QPainter.Antialiasing, True)

        qp.drawRoundedRect(0, 0, window_size.width(), window_size.height(),
                           self.borderRadius, self.borderRadius)

        qp.end()

    def mousePressEvent(self, event):
        if not self.origin:
            self.origin = self.pos()
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        pos = self.pos() + event.pos() - self.mousePos
        if event.buttons() == Qt.LeftButton:
            self.move(pos)


    def mouseReleaseEvent(self, event):
        pos = self.pos() + event.pos() - self.mousePos
        if event.button() == Qt.LeftButton:
            self.move(pos)
            
class QGripLabel(QLabel):
    def __init__(self , parent=None , movable=True):
        super().__init__(parent)
        
        self.addGrips()
        
        self.origin = None
        
        self.movable = movable
        
        self.mousePos = None
        
    def addGrips(self):
        self.setWindowFlags(Qt.SubWindow)
        
        self.grip1 , self.grip2 = QSizeGrip(self) , QSizeGrip(self)
        
        layout = QVBoxLayout()
        
        layout.setContentsMargins(0 , 0 , 0 , 0)
        
        layout.addWidget(self.grip1 , alignment=Qt.AlignTop | Qt.AlignLeft)
        
        layout.addWidget(self.grip2 , alignment=Qt.AlignBottom | Qt.AlignRight)
        
        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        if(not self.movable): return
        
        if not self.origin:
            self.origin = self.pos()
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if(not self.movable): return
        
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.mousePos)

    def mouseReleaseEvent(self, event):
        if(not self.movable): return
        
        if event.button() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.mousePos)