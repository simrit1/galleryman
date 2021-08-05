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


# A rotatable label
class AdvancedLabel(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setPen(Qt.black)

        painter.translate(20, 100)

        painter.rotate(-95)

        painter.drawText(0, 0, "hellos")

        painter.end()


# A Draggable input
class DraggableInput(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("background: transparent;")
        self.origin = None

    def setLimits(self, rect):
        self.limits = rect

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
        with open("/home/strawhat54/.config/galleryman/data/likedPhotos.txt", "r") as f:
            data = f.read()

            if data == "":
                data = []

            else:
                data = loads(data)

        with open("/home/strawhat54/.config/galleryman/data/likedPhotos.txt", "w") as f:
            if self.remove:
                data.remove(self.dir)

            else:
                data.append(self.dir)

            f.write(dumps(data))


# An angled label
class AngledLabel(QWidget):
    _alignment = Qt.AlignLeft | Qt.AlignTop

    def __init__(self, text="", angle=0, parent=None):
        super(AngledLabel, self).__init__(parent)

        self._text = text

        self._angle = angle % 360

        self._radians = radians(-angle)

        self._radiansOpposite = radians(-angle + 90)

    def alignment(self):
        return self._alignment

    def setAlignment(self, alignment):
        if alignment == self._alignment:
            return

        self._alignment = alignment

        self.setMinimumSize(self.sizeHint())

    def angle(self):
        return self._angle

    def setAngle(self, angle):
        angle %= 360

        if angle == self._angle:

            return

        self._angle = angle

        self._radians = radians(-angle)

        self._radiansOpposite = radians(-angle + 90)

        self.setMinimumSize(self.sizeHint())

    def text(self):

        return self._text

    def setText(self, text):

        if text == self._text:

            return

        self._text = text

        self.setMinimumSize(self.sizeHint())

    def sizeHint(self):
        rect = self.fontMetrics().boundingRect(QRect(), self._alignment, self._text)

        sinWidth = abs(sin(self._radians) * rect.width())

        cosWidth = abs(cos(self._radians) * rect.width())

        sinHeight = abs(sin(self._radiansOpposite) * rect.height())

        cosHeight = abs(cos(self._radiansOpposite) * rect.height())

        return QSize(cosWidth + cosHeight, sinWidth + sinHeight)

    def minimumSizeHint(self):

        return self.sizeHint()

    def paintEvent(self, event):

        qp = QPainter(self)

        textRect = self.fontMetrics().boundingRect(QRect(), self._alignment, self._text)

        width = textRect.width()

        height = textRect.height()
        if self._angle <= 90:

            deltaX = 0

            deltaY = sin(self._radians) * width

        elif 90 < self._angle <= 180:

            deltaX = cos(self._radians) * width

            deltaY = sin(self._radians) * width + sin(self._radiansOpposite) * height

        elif 180 < self._angle <= 270:

            deltaX = cos(self._radians) * width + cos(self._radiansOpposite) * height

            deltaY = sin(self._radiansOpposite) * height

        else:

            deltaX = cos(self._radiansOpposite) * height

            deltaY = 0

        qp.translate(0.5 - deltaX, 0.5 - deltaY)

        qp.rotate(-self._angle)

        qp.drawText(self.rect(), self._alignment, self._text)

class QClickableTextEdit(QLineEdit):
    clicked = pyqtSignal(QPoint)
    
    def __init__(self , parent=None):
        super().__init__(parent)
        
    def mousePressEvent(self, e: QMouseEvent) -> None:
        if(e.button() == Qt.LeftButton):
            self.clicked.emit(e.pos())
        
        return super().mousePressEvent(e)

class ResizableLabel(QLabel):
    def __init__(self):
        super().__init__()
        
        self.setGeometry(QRect(500 , 500 , 300 , 300))
        
        layout = QVBoxLayout()
                
        resizerLeft , resizerRight , resizerTop , resizerBottom = QLabel(text=".") , QLabel(text=".") , QLabel(text=".") , QLabel(text=".")
        
        resizerLeft.resizeEvent = self.resizeHandler
        
        resizerBottom.resizeEvent = self.resizeHandler
        
        resizerRight.resizeEvent = self.resizeHandler
        
        resizerTop.resizeEvent = self.resizeHandler
        
        layout.setContentsMargins(0 , 0 , 0 , 0)
        
        layout.addWidget(resizerRight , alignment=Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(resizerLeft , alignment=Qt.AlignTop | Qt.AlignRight)
        
        layout.addWidget(resizerBottom , alignment=Qt.AlignBottom | Qt.AlignLeft)
        
        layout.addWidget(resizerTop , alignment=Qt.AlignBottom | Qt.AlignRight)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
    def resizeHandler(self , event: QResizeEvent):
        print(event.size())

def mouseToThrash(pathDir):
    pass

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
    def __init__(self , parent=None):
        super().__init__(parent)
        
        self.addGrips()
        
        self.origin = None
        
        self.mousePos = None
        
    def addGrips(self):
        self.setWindowFlags(Qt.SubWindow)
        
        grip1 , grip2 = QSizeGrip(self) , QSizeGrip(self)
        
        layout = QVBoxLayout()
        
        layout.setContentsMargins(0 , 0 , 0 , 0)
        
        layout.addWidget(grip1 , alignment=Qt.AlignTop | Qt.AlignLeft)
        
        layout.addWidget(grip2 , alignment=Qt.AlignBottom | Qt.AlignRight)
        
        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        if not self.origin:
            self.origin = self.pos()
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.mousePos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.mousePos)