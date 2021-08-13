from GalleryMan.assets.QtHelpers import Animation, QCustomButton, QSliderMenu
from functools import partial
from PIL import Image , ImageDraw
from PyQt5.QtCore import QParallelAnimationGroup, QPoint, QPointF, QRect, QTimer, Qt, pyqtBoundSignal, pyqtSignal 
from PyQt5.QtGui import QColor, QFont, QKeySequence, QMouseEvent, QPen, QPolygonF
from PyQt5.QtWidgets import QCheckBox, QGraphicsLineItem, QGraphicsSimpleTextItem, QGraphicsView, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QShortcut, QVBoxLayout, QWidget

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
        
        self.shortcut = QShortcut(QKeySequence("Ctrl+X") , self.parent)
        
        self.shortcut.activated.connect(self._breakSupport)
        
        self.parent.setMouseTracking(True)
        
        self.parent.mousePressEvent = lambda event: self.onClick(event)
        
        self.parent.mouseMoveEvent = self.increase
        
        self.undoShortcurt = QShortcut(QKeySequence("Ctrl+Z") , parent)
        
        self.undoShortcurt.activated.connect(self.undoHandler)
        
        self.pointsLocation: list[QPoint] = []
        
        self.lineInited = False
        
        self.isHandleAvail = False
        
        self.breakSupport = False

        self.image = Image.open("./GalleryMan/assets/processed_image.png").convert("RGBA")
        
        self.draw = ImageDraw.ImageDraw(self.image)
        
        self.menu = QSliderMenu(parent)
        
        self.label = QLabel("Right click to connect to the starting point" , self.parent)
        
        self.label.setStyleSheet("font-size: 20px; color: white; background-color: transparent ")
        
        self.label.hide()
        
        self.lineLayersParent = QLabel(parent)
        
        layout = QVBoxLayout()
        
        self.lineLayers = QWidget()
        
        self.scrollArea = QScrollArea()
        
        self.scrollArea.setGeometry(self.lineLayersParent.geometry())
        
        self.scrollArea.setWidget(self.lineLayers)
        
        layout.addWidget(self.scrollArea)
        
        self.lineLayersParent.setLayout(layout)
        
        self.lineLayersParent.setGeometry(QRect(0 , 0 , 0 , 40))
        
        self.lineLayersParent.setStyleSheet("background-color: transparent")
        
        self.width = self.height = 0 
        
        self.count = 1
        
        self.layerLayout = QHBoxLayout()
        
        self.lineLayers.setLayout(self.layerLayout)
        
        self.lines: list[QGraphicsLineItem] = []
        
        self.poped = []
        
        self.label.setGeometry(QRect(0 , 0 , 1000 , 50))
        
        self.showHelp()
        
        self.lineLayersParent.hide()
        
    def _breakSupport(self):
        self.breakSupport = True
        
        try:
            self.lines.pop(self.line)
            
        except:
            pass
        
        self.line.hide()
        
        self.lineLayers.setStyleSheet("background-color: #2E3440")
        
        self.lineLayersParent.move(QPoint(0 , 100))
        
        self.lineLayersParent.show()
        
        self.showToolTip()
    
    def initPointLine(self , position: QPoint , followMouse=False):
        if(self.breakSupport): return
        
        position.setX(position.x() + self.parent.horizontalScrollBar().value())
        
        position.setY(position.y() + self.parent.verticalScrollBar().value())
        
        scene = self.parent.scene()
                
        self.pen = QPen()
        
        self.pen.setColor(QColor(self.config["color"]))
        
        self.pen.setJoinStyle(Qt.RoundJoin)
        
        self.pen.setWidth(int(self.config["width"]))
        
        self.pointsLocation.append(position.__pos__())
        
        self.lineInited = True
        

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
        
        self.scrollArea.setFixedWidth(self.width)
        
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
        
        pen = line.pen()
        
        pen.setColor(QColor("#88C"))
        
        line.setPen(pen)
        
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
            
        checkBox = QCheckBox(text="Straight line")
        
        checkBox.setBaseSize(50 , 50)
        
        checkBox.setStyleSheet("""
            color: #D8DEE9;
            font-family: SauceCodePro Nerd Font;
            font-size: 20px                       
        """)
                
        checkBox.clicked.connect(self.makeItStraight)
        
        self.menu.addMenu("Other options" , checkBox)   
            
        self.menu.move(QPoint(2000 , 0))
        
        self.menu.show()
        
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1877 - self.menu.width(), 0) , 200)
        
        self.animation.start()
    
    def makeItStraight(self):
        # Get the index
        pos = self.lines.index(self.line)
        
        # A variable to check if it is needed to change next one too
        changeNextOne = True
        
        # Check if the line is not the last line
        if(pos == len(self.lines)):
            
            # Dont change the next Line if it is the last line
            changeNextOne = False
        
        line = self.line.line()
        
        if(abs(line.x1() - line.x2()) > abs(line.y1() - line.y2())):
            
            # Set new line
            self.line.setLine(
                line.x1(),
                line.y1(),
                line.x2(),
                line.y1()
            )
        
        else:
            # Set new line
            self.line.setLine(
                line.x1(),
                line.y1(),
                line.x1(),
                line.y2()
            )
        
        # Early return if it was last line
        if(not changeNextOne): return
        
        nextLine = self.lines[pos + 1]
        
        nextLine.setLine(
            self.line.line().x2(),
            self.line.line().y2(),
            nextLine.line().x2(),
            nextLine.line().y2()
        )
        
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
    
    def showToolTip(self):
        polygon = QPolygonF()
        
        pen = QPen()
        
        pen.setColor(QColor("#2E3440"))
        
        for points in [QPoint(100 , 100 - 50) , QPoint(700 , 100 - 50) , QPoint(700 , 160 - 50 - 10) , QPoint(400 , 160 - 50 - 10) , QPoint(390 , 170 - 50 - 10) , QPoint(380 , 160 - 50 - 10) , QPoint(280 , 160 - 50 - 10) , QPoint(100 , 160 - 50 - 10) , QPoint(100 , 100 - 50 + 10)]:
            polygon.append(QPointF(points))
            
        self.tooltip = self.parent.scene().addPolygon(polygon , pen)
        
        self.tooltip.setBrush(QColor("#2E3440"))
        
        pen = QPen()
        
        pen.setColor(QColor("#88C0D0"))
        
        pen.setWidth(-1)
        
        font = QFont("Comfortaa" , 15)
        
        text = QGraphicsSimpleTextItem("Here are your layers, click the layer to customize" , self.tooltip)
        
        text.setBrush(QColor("#88C0D0"))
        
        text.setPen(pen)
        
        text.setFont(font)
        
        rect = text.boundingRect()
        
        bounding = self.tooltip.boundingRect()
            
        rect.moveCenter(QPointF(bounding.center().x() , bounding.center().y() - 5))
        
        text.setPos(rect.topLeft())        
        
        self.animation = QParallelAnimationGroup()
        
        self.animation.addAnimation(Animation.fadingAnimation(Animation , self.tooltip , 200 , True))   
        
        self.animation.start()
        
        self.tooltip.setPos(QPoint(555 , 555))

        
    def showHelp(self):
        def run_second():
            self.animation = Animation.fadingAnimation(Animation , self.help , 300)
            
            # self.timer = QTimer(self.parent)
            
            # self.timer.start(700)
            
            # self.timer.setSingleShot(True)
            
            self.animation.finished.connect(self.help.hide)
            
            self.animation.start()
            
            # self.timer.timeout.connect(self.animation.start)
            
            # self.tooltiptimer = QTimer(self.parent)
            
            # self.tooltiptimer.setSingleShot(True)
            
            # self.tooltiptimer.start(2000)
            
            # self.animation.finished.connect(self.showToolTip)
            
            # self.tooltiptimer.timeout.connect(self.hideToolTip)
        
        self.help = QLabel(self.parent)
        
        self.help.setGeometry(self.parent.geometry())
        
        helpLayouts = QVBoxLayout()
        
        for _ in range(25):
            sep = QLabel()
            
            sep.setStyleSheet("background-color: transparent")
            
            sep.setFixedHeight(10)
            
            helpLayouts.addWidget(sep)
        
        for data in ["1. Press Ctrl+S to save and exit" , "2. Click and drag the mouse to draw lines", "3. Press Ctrl+X to customize the lines drawn"]:
            label = QLabel(data , None)
            
            label.setFixedHeight(50)
            
            label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
            
            label.setStyleSheet("""background-color: transparent; font-size: 20px""")
            
            helpLayouts.addWidget(label)
            
        okay = QCustomButton("Okay!" , None).create()
        
        okay.setStyleSheet("background-color: #2E3440; border: 1px solid white")
        
        okay.clicked.connect(run_second)
        
        okay.setFixedSize(200 , 50)
        
        helpLayouts.addWidget(okay , alignment=Qt.AlignCenter | Qt.AlignCenter)
        
        for _ in range(25):
            sep = QLabel()
            
            sep.setStyleSheet("background-color: transparent")
            
            sep.setFixedHeight(10)
            
            helpLayouts.addWidget(sep)
            
            
        self.help.setLayout(helpLayouts)
                
        self.help.setStyleSheet("""
            background-color: rgba(46, 52, 64, 160);
            font-size: 30px;                        
        """)
        
        self.help.show()
        
        self.animation = Animation.fadingAnimation(Animation , self.help , 300 , True)
        
        # self.animation.finished.connect(run_second)
        
        self.animation.start()
        
    def hideToolTip(self):
        self.animation = Animation.fadingAnimation(Animation , self.tooltip , 200)
        
        self.animation.start()

class PolyGon(doodleShape):
    def __init__(self , parent):
        super().__init__(parent)
        
    def onClick(self, event: QMouseEvent):
        self.initPointLine(event.pos() , True)
        
    def saveDrawing(self , points):
        pass