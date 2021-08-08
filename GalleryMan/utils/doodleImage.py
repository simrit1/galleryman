from GalleryMan.assets.QtHelpers import Animation, QCustomButton, QSliderMenu
from functools import partial
from PIL import Image , ImageDraw
from PyQt5.QtCore import QPoint, QRect, Qt, pyqtBoundSignal, pyqtSignal 
from PyQt5.QtGui import QColor, QCursor, QKeySequence, QMouseEvent, QPen, QTextCursor
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsLineItem, QGraphicsScene, QGraphicsView, QHBoxLayout, QLabel, QLineEdit, QPushButton, QShortcut
import random

class customLineItem(QGraphicsLineItem):
    changeStyles = pyqtBoundSignal(QGraphicsLineItem)
    
    def __init__(self , x1 , y1 , x2 , y2 , pen , callback):
        super().__init__(x1 , y1 , x2 , y2)
        
        self.setPen(pen)
        
        self.enableMouseTracking = False
        
        self.callback = callback

class doodleShape:
    drawingCompleted = pyqtSignal(list)
    
    def __init__(self , parent: QGraphicsView):
        self.parent = parent
            
        self.config = {
            "width": 5,
            "color": "#88C0D0",
            "border-radius": 10,
            "outline-color": "#2E3440",
            "outline-width": 5
        }
        
        self.parent.setMouseTracking(True)
        
        self.parent.mousePressEvent = lambda event: self.onClick(event)
        
        self.parent.mouseMoveEvent = self.increase
        
        self.undoShortcurt = QShortcut(QKeySequence("Ctrl+Z") , parent)
        
        self.undoShortcurt.activated.connect(self.undoHandler)
        
        self.pointsLocation: list[QPoint] = []
        
        self.lineInited = False
        
        self.isHandleAvail = False
        
        self.breakSupport = False

        self.image = Image.open("GalleryMan/assets/processed_image.png").convert("RGBA")
        
        self.draw = ImageDraw.ImageDraw(self.image)
        
        self.menu = QSliderMenu(parent)
        
        self.label = QLabel("Right click to connect to the starting point" , self.parent)
        
        self.label.setStyleSheet("font-size: 20px; color: white; background-color: transparent ")
        
        self.label.hide()
        
        self.lineLayers = QLabel(parent)
        
        self.lineLayers.setGeometry(QRect(0 , 0 , 0 , 40))
        
        self.lineLayers.setStyleSheet("background-color: transparent")
        
        self.width = self.height = 0 
        
        self.count = 1
        
        self.layerLayout = QHBoxLayout()
        
        self.lineLayers.setLayout(self.layerLayout)
        
        self.lines = []
        
        self.poped = []
        
        self.label.setGeometry(QRect(0 , 0 , 1000 , 50))
    
    def flood(self , event: QMouseEvent):
        
        ImageDraw.floodfill(self.image , (event.x() , event.y()) , (255 , 255 , 0 , 255) , thresh=50)
        
        self.image.save("LOLCAT.PNG")
    
    def initPointLine(self , position: QPoint , followMouse=False):
        if(self.breakSupport): return
        
        position.setX(position.x() + self.parent.horizontalScrollBar().value())
        
        position.setY(position.y() + self.parent.verticalScrollBar().value())
        
        scene = self.parent.scene()
        
        if(self.pointsLocation):
            firstPointLocation = self.pointsLocation[0]
                                 
            if(abs(position.x() - firstPointLocation.x()) <= 30 and abs(position.y() - firstPointLocation.y()) <= 30):
                self.isHandleAvail = True
            else:
                self.isHandleAvail = False
                
        self.pen = QPen()
        
        self.pen.setColor(QColor(self.config["color"]))
        
        self.pen.setJoinStyle(Qt.RoundJoin)
        
        self.pen.setWidth(int(self.config["width"]))
        
        self.pointsLocation.append(position.__pos__())
        
        self.lineInited = True
        
        if(self.isHandleAvail):
            self.breakSupport = True
        
        else:
            self.line = customLineItem(position.x() , position.y() , position.x() + 0.5 , position.y() + 0.5, self.pen , self.updateSingleLine)
            
            scene.addItem(self.line)
            
            self.lines.append(self.line)
            
            button = QCustomButton(str(self.count) , None).create()
                
            button.setFixedSize(30 , 30)
            
            button.setStyleSheet("""
                color: #D8DEE9;
                font-size: 20px;
            """)
            
            button.clicked.connect(partial(self.updateSingleLine , self.line))
            
            self.width += len(str(self.count)) * 30
            
            self.lineLayers.setFixedWidth(self.width)
            
            self.layerLayout.addWidget(button , alignment=Qt.AlignCenter | Qt.AlignCenter)
            
            self.count += 1
                    
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
        
    def updateSingleLine(self , line: QGraphicsLineItem):
        self.line = line
        
        self.menu.hide()
        
        self.menu = QSliderMenu(self.parent)
        
        self.manageMenu()
                
    def manageMenu(self):
        stylesheet = """
            border: 1px solid #4C566A;
            padding: 10px;
            padding-left: 10px;
            color: white;
        """
        
        for name in ["Width" , "Color" , "Border Radius" , "Outline Color" , "Outline Width"]:
            inputBox = QLineEdit()
            
            inputBox.setPlaceholderText(name)
            
            inputBox.setFixedHeight(50)
            
            inputBox.setStyleSheet(stylesheet)
            
            inputBox.textChanged.connect(partial(self.update , name.lower().replace(' ' , '-') , inputBox))
            
            self.menu.addMenu(name , inputBox)
            
        self.menu.move(QPoint(2000 , 0))
        
        self.menu.show()
        
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1877 - self.menu.width(), 0) , 200)
        
        self.animation.start()
    
    def update(self , Sclass , inputBox):
        self.config[Sclass] = inputBox.text()  
        
        self.pen = QPen()  
        
        self.pen.setColor(QColor(self.config["color"]))
        
        self.pen.setWidth(int(self.config["width"]))
        
        self.line.setPen(self.pen)
        
    def undoHandler(self): 
        self.increase(self.parent.cursor().pos())
                
        self.lines[-1].hide()
        
        self.poped.append(self.lines.pop(-1))
        
        self.line = self.lines[-1]
    
    # def redohandler(self):
    #     line = self.line.line()
        
    #     new_line = self.poped.pop(-1)
        
    #     self.line.setLine(line.x1() , line.y1() , new_line.line().x2() , new_line.line().y2())
        
    #     self.poped[-1].show()
        
    #     self.lines.append(new_line)
        
    #     self.line = new_line
        
    #     self.increase(self.parent.cursor().pos())

# ----------------- SUBCLASSES -------------------------

class PolyGon(doodleShape):
    def __init__(self , parent):
        super().__init__(parent)
        
    def onClick(self, event: QMouseEvent):
        self.initPointLine(event.pos() , True)
        
    def saveDrawing(self , points):
        pass