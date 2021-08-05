from PIL import Image , ImageDraw
from PyQt5.QtCore import QPoint, QRect, Qt, pyqtSignal 
from PyQt5.QtGui import QColor, QCursor, QMouseEvent, QPen, QTextCursor
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsScene, QGraphicsView, QLabel, QPushButton


class doodleShape:
    drawingCompleted = pyqtSignal(list)
    
    def __init__(self , parent: QGraphicsView):
        self.parent = parent
        
        self.parent.setMouseTracking(True)
        
        self.parent.mousePressEvent = lambda event: self.onClick(event)
        
        self.parent.mouseMoveEvent = self.increase
        
        self.pointsLocation: list[QPoint] = []
        
        self.lineInited = False
        
        self.isHandleAvail = False
        
        self.breakSupport = False

        self.image = Image.open("GalleryMan/assets/processed_image.png").convert("RGBA")
        
        self.draw = ImageDraw.ImageDraw(self.image)
        
        self.label = QLabel("Right click to connect to the starting point" , self.parent)
        
        self.label.setStyleSheet("font-size: 20px; color: white; background-color: transparent ")
        
        self.label.hide()
        
        self.label.setGeometry(QRect(0 , 0 , 1000 , 50))
    
    def flood(self , event: QMouseEvent):
        
        ImageDraw.floodfill(self.image , (event.x() , event.y()) , (255 , 255 , 0 , 255) , thresh=50)
        
        self.image.save("LOLCAT.PNG")
    
    def initPointLine(self , position: QPoint , followMouse=False):
        if(self.breakSupport): 
            self.flood(position)
            
            return
        
        try:
            self.draw.line((self.line.line().x1() , self.line.line().y1() , self.line.line().x2() , self.line.line().y2()))
            
            self.image.save("LOLCAT.PNG")
        except:
            pass
                
        
        position.setX(position.x() + self.parent.horizontalScrollBar().value())
        
        position.setY(position.y() + self.parent.verticalScrollBar().value())
        
        scene = self.parent.scene()
        
        if(self.pointsLocation):
            firstPointLocation = self.pointsLocation[0]
                                 
            if(abs(position.x() - firstPointLocation.x()) <= 30 and abs(position.y() - firstPointLocation.y()) <= 30):
                self.isHandleAvail = True
            else:
                self.isHandleAvail = False
                
        pen = QPen()
        
        pen.setColor(QColor("#88C0D0"))
        
        pen.setJoinStyle(Qt.RoundJoin)
        
        pen.setWidth(3)
        
        self.pointsLocation.append(position.__pos__())
        
        self.lineInited = True
        
        if(self.isHandleAvail):
            self.breakSupport = True
        
        else:
            self.line = scene.addLine(position.x() , position.y() , position.x() + 0.5 , position.y() + 0.5, pen)
            
        self.line.setFlag(QGraphicsItem.ItemIsMovable)
            
    def increase(self , event: QMouseEvent):
        if(not self.lineInited or self.breakSupport): return
        
        x = event.x() + self.parent.horizontalScrollBar().value()
        
        y = event.y() + self.parent.verticalScrollBar().value()
        
        self.line.setLine(self.line.line().x1() , self.line.line().y1() , x , y)
                
        firstPointLocation = self.pointsLocation[0]
                             
        if(abs(x - firstPointLocation.x()) <= 10 or abs(y - firstPointLocation.y()) <= 10):            
            self.label.move(x , y)            
        else:
            self.isHandleAvail = False
            
            self.label.hide()


# ----------------- SUBCLASSES -------------------------

class PolyGon(doodleShape):
    def __init__(self , parent):
        super().__init__(parent)
        
    def onClick(self, event: QMouseEvent):
        self.initPointLine(event.pos() , True)
        
    def saveDrawing(self , points):
        pass