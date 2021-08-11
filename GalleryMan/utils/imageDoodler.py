# Importing the modules
from GalleryMan.utils.doodleImage import PolyGon
from functools import partial
from math import atan2, pi
from PIL import Image, ImageDraw
from PyQt5.QtCore import (
    QPoint,
    QRect,
    QRectF,
    QSize,
    Qt,
)
from PyQt5.QtGui import (
    QColor,
    QImage,
    QKeySequence,
    QMouseEvent,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt5.QtWidgets import (
    QCheckBox,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QShortcut,
)
from GalleryMan.assets.QtHelpers import (
    Animation,
    QCustomButton,
    QSliderMenu,
)
from GalleryMan.utils.helpers import *

class QClickableTextEdit(QLineEdit):
    clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.clicked.emit()
        
        return super().mousePressEvent(a0)

class doodleImageItems:
    """Base class for every doodle item"""
    
    def __init__(self , parent , renderArea , outParent):
        self.parent = parent

        self.renderArea = renderArea

        self.outParent = outParent
        
        self.pointsPath = []
                
        self.graphics = QGraphicsView(parent)

        self.graphics.setGeometry(QRect(0 , 0 , 1980 , 1080))
        
        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scene = QGraphicsScene()
        
        self.graphics.setScene(self.scene)
        
        self.menu = QSliderMenu(self.parent)
        
        self.image = Image.open("GalleryMan/assets/processed_image.png").convert("RGBA")
        
        self.currentIndex = -1
        
        self.undoShortcut = QShortcut(QKeySequence("Ctrl+Z") , self.parent)
        
        self.undoShortcut.activated.connect(self.undoHandler)
        
        self.redoShortcut = QShortcut(QKeySequence("Ctrl+Y") , self.parent)
        
        self.redoShortcut.activated.connect(self.redoHandler)
        
        self.continueNext = QShortcut(QKeySequence("Ctrl+S") , self.parent)
                
        self.graphics.show()
    
    def undoHandler(self):
        pass
    
    def redoHandler(self):
        pass
    
    def removeMenu(self, startAni):
        self.animation = Animation.movingAnimation(
            Animation, self.menu, QPoint(2000, 0), 200
        )
        
        self.menu = QSliderMenu(self.parent)
        
        self.animation.finished.connect(self.menu.hide)

        self.animation.start()
        
        startAni.show()
    
    def createMenu(self , items: list , stylesheet: str , updater):
        for name in items:
            textEdit = QLineEdit()
            
            textEdit.setFixedHeight(50)
            
            textEdit.setPlaceholderText(name)
            
            textEdit.setStyleSheet(stylesheet)
            
            textEdit.textChanged.connect(partial(updater, name.lower().replace(' ' , '-'), textEdit))
            
            self.menu.addMenu(name , textEdit)
    
class doodleFreeHand(doodleImageItems):
    def __init__(self, parent, renderArea, outParent):
        super().__init__(parent, renderArea, outParent)
        
    
    def showGraphics(self):
        self.points = []
        
        self.styles = []
        
        self.deleted = []
        
        # Config to store all the details of the new drawing
        self.config = {
            "width": 2,
            "height": 2,
            "color": "#88C0D0",
            "outline": "#2E3440",
            "outline-width": -1,
            "border-radius": 0,
        }
    
        
        # Add the image
        self.pixmap = self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
                
        # Slider menu where the user can change the brush
        self.menu = QSliderMenu(self.parent)
        
        # Button which will toggle the menu
        self.startAni = QCustomButton(" ", self.parent).create()
        
        # Styles and positioning correctly
        self.startAni.setGeometry(QRect(1770, 5, 50, 50))

        self.startAni.setStyleSheet(
            "border: 0; background-color: transparent; float: left"
        )
        
        # Open menu onclick
        self.startAni.clicked.connect(partial(self.manageMenu, self.startAni))
        
        # Show the button
        self.startAni.show()
        
        # Call respect function when the user clicks and drags to draw points
        self.graphics.mousePressEvent = lambda event: self.mouseHandler(
            event, "pressEvent"
        )

        self.graphics.mouseMoveEvent = lambda event: self.mouseHandler(
            event, "moveEvent"
        )
        
        # Stop drawing when the user stops stops dragging
        self.graphics.mouseReleaseEvent = self._reset
        
        self.continueNext.activated.connect(self.printOut)

        with open("/home/strawhat54/.galleryman/data/helpReq.txt") as f:
            data = loads(f.read())
        
        if(data["freeHand"] == "True"):
            self.showHelp()
            
    def _reset(self, _):
        self.pressed = False

    def mouseHandler(self, event: QMouseEvent, type):
        # If the user clicks, the set the pressed varible to true
        if type == "pressEvent":
            self.pressed = True
        else:
            # If the user hasnt clicked yet, but still drags, dont draw anyhting
            if not self.pressed:
                return
        
        # Check if the mouse click does not exceed the limit
        if event.x() < 0 or event.y() < 0:
            return
        
        # Make the x and y position correct according to the scroll value
        x = event.x() + self.graphics.horizontalScrollBar().value()

        y = event.y() + self.graphics.verticalScrollBar().value()
        
        # Create a pen for drawing according to the requirements
        pen = QPen(
            QColor(self.config["outline"]),
            1,
            Qt.SolidLine,
            Qt.FlatCap,
            Qt.MiterJoin,
        )
        
        # Set the font size
        pen.setWidth(int(self.config["outline-width"]))
        
        # Painter
        self.path = QPainterPath()
                
        self.path.addRoundedRect(
            QRectF(x, y, int(self.config["width"]), int(self.config["height"])),
            int(self.config["border-radius"]),
            int(self.config["border-radius"]),
        )
        
        # Append the details of the point to the list
        self.styles.append([x, y] + list(self.config.values()))
        
        
        # Add the drawing on the scene
        self.rect = self.scene.addPath(self.path, pen)
        
        # Set the fill color
        self.rect.setBrush(QColor(self.config["color"]))
        
        self.points.append(self.rect)
        
    def manageMenu(self, startAni: QPushButton = None):
        stylesheet = """
            border: 1px solid #4C566A;
            padding: 10px;
            padding-left: 10px;
            color: white;
        """
        
        # Hide the toggler
        startAni.hide()
        
        # Add a cross on top of the menu, which will close the menu
        layout = QHBoxLayout()
        
        # Create a button with beautiful stylings <3
        widget = QCustomButton(text="" , window=None).create()
        
        widget.setStyleSheet(startAni.styleSheet())
        
        widget.setFixedSize(QSize(150 , 50))
        
        widget.clicked.connect(lambda : self.removeMenu(startAni))
        
        # Add the cross button, on top right
        layout.addWidget(widget , alignment=Qt.AlignTop | Qt.AlignRight)
        
        # Add to menu
        self.menu.addMenu("" , layout , True)
        
        # Fill the menu with all the options os styling
        self.createMenu(
            ["Width" , "Height" , "Color" , "Outline" , "Outline Width" , "Border Radius"],
            stylesheet,
            self.update
        )
        
        # Show the menu
        self.menu.show()
        
        # Move the menu outside the screen
        self.menu.move(QPoint(2000, 0))
        
        # Move it inside with a animation
        self.animation = Animation.movingAnimation(
            Animation, self.menu, QPoint(1900 - self.menu.width(), 0), 300
        )
        
        # Start the animation
        self.animation.start()
    
    def update(self, key, input: QLineEdit):
        value = input.text()

        self.config[key] = value
        
    def undoHandler(self):
        try:
            self.points[-1].hide()
            
            self.styles.pop(-1)
            
            self.deleted.append(self.points.pop(-1))
        except Exception as e:
            pass
        
    def redoHandler(self):
        try:
            self.deleted[-1].show()
            
            self.styles.append(-1)
            
            self.points.append(self.deleted.pop(-1))
        except:
            pass
        
        return super().redoHandler()
    
    def printOut(self):
        drawing = ImageDraw.ImageDraw(self.image)
    
        for (
            x,
            y,
            width,
            height,
            color,
            outlineColor,
            outlineWidth,
            border_radius,
        ) in self.styles:
            
            outlineWidth = 0 if int(outlineWidth) < 0 else int(outlineWidth)

            x, y, width, height = int(x), int(y), int(width), int(height)

            drawing.rounded_rectangle(
                (x, y, x + width, y + height),
                border_radius,
                color,
                outlineColor,
                outlineWidth,
            )

        self.image.save("GalleryMan/assets/processed_image.png")

        self.renderArea.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        self.animation = Animation.fadingAnimation(Animation, self.graphics, 300)

        self.animation.finished.connect(self.graphics.hide)

        self.animation.start()
        
        # Reset Stylings
        self.styles = {}
        
        # Remove the shortcut
        self.continueNext.setKey(QKeySequence())
        
    def showHelp(self):        
        self.helpEllipse = self.scene.addEllipse(
            self.graphics.width() - 100,
            50,
            50, 50, QColor("#88C0D0"), 
        )
                
# Rect class
class doodlerectItem(doodleImageItems):
    def __init__(self, parent, renderArea, outParent):
        super().__init__(parent, renderArea, outParent)
        
    def createGraphics(self):
        self.config = {
            "background-color": "#2E3440",
            "border-color": "#2E3440",
            "border-width": 40,
            "border-radius": 0,
        }
        
        
        self.pixmap = self.scene.addPixmap(QPixmap('GalleryMan/assets/processed_image.png'))

        def updateConfig(Sclass , label: QLineEdit):
            if(Sclass != ""): self.config[Sclass] = label.text()

            self.rectangle.setStyleSheet(
                """
                QLabel{{
                    background-color: {color};
                    border: {width}px solid {colorB};
                    border-radius: {rad}     
                }}
                
                QSizeGrip{{
                    background-color: {color};
                    border-radius: {rad}
                }}
            """.format(
                    color=self.config["background-color"],
                    width=self.config["border-width"],
                    colorB=self.config["border-color"],
                    rad=self.config["border-radius"],
                )
            )
            
        # Create a grip label 
        self.rectangle = QGripLabel()
        
        # Add to scene
        self.scene.addWidget(self.rectangle)
    
        # Set geometry
        self.rectangle.setGeometry(QRect(100, 100, 500, 500))
        
        # Show
        self.rectangle.show()        
        
        # Set stylings according to te config
        updateConfig("" , None)
        
        self.menu = QSliderMenu(self.graphics)
        
        self.continueNext.activated.connect(partial(self.drawRectOnImage, self.rectangle))
        
        stylesheet = """
            border: 1px solid #4C566A;
            padding: 10px;
            font-size: 12px;
            padding-left: 10px;
            color: white;
        """
        
        crossLabel = QVBoxLayout()
        
        cross = QLabel()
        
        cross.setFixedSize(QSize(50 , 50))
        
        cross.setText("X")
        
        crossLabel.addWidget(cross , alignment=Qt.AlignTop | Qt.AlignLeft)
        
        self.menu.addMenu("" , crossLabel , True)
            
        self.createMenu(["Background Color", "Border Color", "Border Width", "Border Radius"] , stylesheet , updateConfig)
        

        def callback():
            self.menu.show()

            self.menu.move(QPoint(2000, 0))

            self.animation = Animation.movingAnimation(
                Animation, self.menu, QPoint(1900 - self.menu.width(), 0), 300
            )

            self.animation.start()

        startAni = QCustomButton(" ", self.graphics).create()

        startAni.setGeometry(QRect(1700, 0, 100, 100))

        startAni.setStyleSheet("""
            background-color: transparent;
            color: #88C0D0;
        """)

        startAni.show()

        startAni.clicked.connect(callback)
    
    def drawRectOnImage(self, label: QGripLabel):
        def callback():
            self.graphics.hide()
            
            self.renderArea.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))
            
        self.image = Image.open("GalleryMan/assets/processed_image.png").convert("RGBA")

        draw = ImageDraw.ImageDraw(self.image)

        draw.rounded_rectangle(
            (
                label.geometry().x(),
                label.geometry().y(),
                label.geometry().x() + label.geometry().width(),
                label.geometry().y() + label.geometry().height(),
            ),
            int(self.config["border-radius"]),
            self.config["background-color"],
            self.config["border-color"],
            int(self.config["border-width"]),
        )

        self.image.save("GalleryMan/assets/processed_image.png")
        
        self.animation = Animation.fadingAnimation(Animation , self.graphics , 300)
        
        self.animation.finished.connect(callback)
        
        self.animation.start()
        
        self.continueNext.setKey(QKeySequence())

class doodleLineItem(doodleImageItems):
    def __init__(self, parent, renderArea, outParent):
        super().__init__(parent, renderArea, outParent)
        
        self.posOptions = []
        
    def createGraphics(self):
        self.pixmap = self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        def makeItEven(checked: bool):
            self.lineRect.setLine(self.lineRect.line().x1() , self.lineRect.line().y1() , self.lineRect.line().x2() , self.lineRect.line().y1())
            
            self.posOptions[0].setText("{} x {}".format(int(self.lineRect.line().x1()) , int(self.lineRect.line().y1())))
            
            self.posOptions[0].setText("{} x {}".format(int(self.lineRect.line().x2()) , int(self.lineRect.line().y2())))

        self.scene.clear()

        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        pen = QPen()

        pen.setColor(QColor("#88C0D0"))

        pen.setStyle(Qt.SolidLine)

        self.lineRect = self.scene.addLine(500, 500, 700, 700, pen)

        self.menu = QSliderMenu(self.parent)

        stylesheet = """
            border: 1px solid #4C566A;
            padding: 10px;
            font-size: 12px;
            padding-left: 10px;
            color: white;
        """

        self.config = {
            "start-position": 500,
            "end-position": 500,
            "width": 1,
            "color": "#88C0D0",
        }
        
        crossLabel = QVBoxLayout()
        
        cross = QLabel()
        
        cross.setFixedSize(QSize(50 , 50))
        
        cross.setText("X")
        
        crossLabel.addWidget(cross , alignment=Qt.AlignTop | Qt.AlignLeft)
        
        self.menu.addMenu("" , crossLabel , True)

        for name, propertyName in zip(
            ["Start Position", "End Position", "Color", "Width"],
            ["start-position", "end-position", "color", "width"],
        ):
            inputBox = QClickableTextEdit()

            inputBox.setProperty("class", propertyName)

            if name in ["Start Position", "End Position"]:
                inputBox.setPlaceholderText("Click To Choose")

                inputBox.clicked.connect(partial(self.askForPos, inputBox , None))
                
                self.posOptions.append(inputBox)

            else:
                inputBox.setPlaceholderText(name)

            inputBox.setFixedHeight(50)

            inputBox.setStyleSheet(stylesheet)

            inputBox.textChanged.connect(partial(self.update, propertyName, inputBox))

            self.menu.addMenu(name, inputBox)
        
        checkBox = QCheckBox(text="Straight line")
        
        checkBox.setBaseSize(50 , 50)
        
        checkBox.setStyleSheet("""
            color: #D8DEE9;
            font-family: SauceCodePro Nerd Font;
            font-size: 20px                       
        """)
        
        self.continueNext.activated.connect(self.drawLineOnImage)
        
        checkBox.clicked.connect(makeItEven)
        
        self.menu.addMenu("Other options" , checkBox)    
        
        self.graphics.show()

        self.menu.show()

        self.animation = Animation.movingAnimation(
            Animation, self.menu, QPoint(1870 - self.menu.width(), 0), 300
        )

        self.animation.start()

    def askForPos(self, inputt: QLineEdit, cordinates: QPoint):
        self.animation = Animation.movingAnimation(
            Animation, self.menu, QPoint(2000, 0), 300
        )

        self.animation.start()

        self.outerLabel = QLabel(self.graphics)

        self.outerLabel.setGeometry(self.graphics.geometry())

        self.outerLabel.setText("Click on the point")

        self.outerLabel.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        self.outerLabel.show()

        self.outerLabel.setStyleSheet("font-size: 30px; background-color: #2E344050")

        self.graphics.setCursor(Qt.CrossCursor)

        self.outerLabel.mousePressEvent = lambda pos: self.setPos(pos, inputt)

    def setPos(self, pos, inputt: QLineEdit):
        inputt.setText("{} x {}".format(pos.x(), pos.y()))

        self.outerLabel.hide()

        classS = inputt.property("class")

        if classS == "start-position":
            self.lineRect.setLine(
                pos.x() + self.graphics.horizontalScrollBar().value(),
                pos.y() + self.graphics.verticalScrollBar().value(),
                self.lineRect.line().x2(),
                self.lineRect.line().y2(),
            )
        else:
            self.lineRect.setLine(
                self.lineRect.line().x1(),
                self.lineRect.line().y1(),
                pos.x() + self.graphics.horizontalScrollBar().value(),
                pos.y() + self.graphics.verticalScrollBar().value(),
            )

        self.update(inputt.property("class"), inputt)

        self.graphics.setCursor(Qt.ArrowCursor)

        self.animation = Animation.movingAnimation(
            Animation, self.menu, QPoint(1870 - self.menu.width(), 0), 300
        )

        self.animation.start()

    def updateStylings(self):
        pen = QPen(
            QColor(self.config["color"]),
            int(self.config["width"]),
            Qt.SolidLine,
        )

        try:
            self.lineRect.setPen(pen)
        except:
            pass
        
    def update(self, key, input: QLineEdit):
        value = input.text()

        self.config[key] = value
        
        self.updateStylings()
    
    def drawLineOnImage(self):
        draw = ImageDraw.Draw(self.image)
        
        lineGeo = self.lineRect.line()
        
        draw.line((
            lineGeo.x1(),
            lineGeo.y1(),
            lineGeo.x2(),
            lineGeo.y2()
        ) , self.config["color"] , int(self.config["width"]))
        
        self.image.save("GalleryMan/assets/processed_image.png")
        
        self.animation = Animation.fadingAnimation(Animation , self.graphics , 200)
        
        self.animation.finished.connect(self.graphics.hide)
        
        self.animation.start()
        
        self.renderArea.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        self.continueNext.setKey(QKeySequence())

class doodleEllipse(doodleImageItems):
    def __init__(self, parent, renderArea, outParent):
        super().__init__(parent, renderArea, outParent)
        
    def createGraphics(self):
        self.graphics.show()
        
        def responser(event: QResizeEvent):
            button.move(QPoint(event.size().width() - button.width(), button.y()))

            if not self.menu.pos() == self.originalPos:
                self.menuOpeningPos = QPoint(
                    event.size().width() - self.menu.width(), 0
                )

                button.click()

        self.menu = QSliderMenu(self.parent)

        self.menuOpeningPos = QPoint(1870 - self.menu.width(), 0)

        self.originalPos = QPoint(2000, 0)

        self.scene.clear()

        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        pen = QPen()

        pen.setColor(QColor("#88C0D0"))

        stylesheet = """
            border: 1px solid #4C566A;
            padding: 10px;
            font-size: 12px;
            padding-left: 10px;
            color: white;
        """

        self.config = {
            "radius": 10,
            "outline-color": "#2E3550",
            "color": "#88C0D0",
            "outline": "#2E3440",
            "outline-width": 10,
        }
        
        self.continueNext.activated.connect(self.drawCircleOnImage)

        self.pen = QPen(QColor(self.config["outline-color"]), int(self.config["outline-width"]), Qt.SolidLine)

        self.ecllipse = self.scene.addEllipse(
            500, 500, self.config["radius"] * 2, self.config["radius"] * 2, self.pen
        )

        self.ecllipse.setFlag(QGraphicsItem.ItemIsMovable)

        self.ecllipse.setBrush(QColor(self.config["color"]))
        
        crossLabel = QVBoxLayout()
        
        cross = QLabel()
        
        cross.setFixedSize(QSize(50 , 50))
        
        cross.setText("X")
        
        crossLabel.addWidget(cross , alignment=Qt.AlignTop | Qt.AlignLeft)
        
        self.menu.addMenu("" , crossLabel , True)
        
        self.createMenu(["Radius", "Color", "Outline", "Outline Width"] , stylesheet , self.update_my_styles)

        self.parent.resizeEvent = responser

        button = QCustomButton("S", self.parent).create()

        button.setGeometry(QRect(self.parent.width() - 100, 0, 100, 100))

        button.show()
        
        button.clicked.connect(self.showMenu)
        
        self.continueNext.activated.connect(self.drawCircleOnImage)

        self.menu.move(self.originalPos)
    
    def showMenu(self):
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1870 - self.menu.width(), 0) , 200)
        
        self.animation.start()
        
        self.isMenuOpen = True    
    
    def drawCircleOnImage(self):
        # Get the geometry
        area = self.graphics.geometry()
        
        # Parse the image 
        image = QImage(area.size(), QImage.Format_ARGB32_Premultiplied)
        
        painter = QPainter(image)
        
        self.scene.render(painter, QRectF(image.rect()), QRectF(area))
        
        painter.end()
        
        image.save("GalleryMan/assets/processed_image.png")
        
        self.animation = Animation.fadingAnimation(Animation , self.graphics , 200)
        
        self.animation.finished.connect(self.graphics.hide)
        
        self.animation.start()
        
        self.renderArea.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))
    
        self.continueNext.setKey(QKeySequence())
        
    def update_my_styles(self, key, label):
        try:
            self.config[key] = int(label.text())
        except:
            self.config[key] = label.text()

        self.ecllipse.setBrush(QColor(self.config["color"]))

        self.ecllipse.setPen(
            QPen(QColor(self.config["outline"]), int(self.config["outline-width"]))
        )

        self.ecllipse.setRect(
            500, 500, int(self.config["radius"] * 2), int(self.config["radius"] * 2)
        )

class doodleImage:
    def __init__(self, parent, renderArea, outParent) -> None:
        self.parent = parent

        self.renderArea = renderArea

        self.outParent = outParent

        self.pressed = False
        
        self.posOptions = []

        self.image = Image.open("GalleryMan/assets/processed_image.png").convert("RGBA")

        self.draw = ImageDraw.ImageDraw(self.image)

        self.graphics = QGraphicsView(self.parent)

        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.styles = {}
        
        self.tempStyles = {}
        
        self.currentIndex = -1

        self.scene = QGraphicsScene(self.parent)

        self.graphics.setScene(self.scene)
        
        self.shortcut = QShortcut(QKeySequence("Ctrl+S") , self.graphics)
        
        self.shortcut.activated.connect(self.printOut)

        self.pixmap = self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        self.graphics.setGeometry(QRect(0, 0, 1980, 1080))

        self.config = {
            "width": 2,
            "height": 2,
            "color": "#88C0D0",
            "outline": "#2E3440",
            "outline-width": -1,
            "border-radius": 10,
        }

    def freeHand(self):
        line = doodleFreeHand(self.parent , self.renderArea , self.outParent)
        
        line.showGraphics()

    def line(self):
        lineItem = doodleLineItem(self.parent , self.renderArea , self.outParent)
        
        lineItem.createGraphics()

    def circle(self):
        ellipse = doodleEllipse(self.parent , self.renderArea , self.outParent)
        
        ellipse.createGraphics()
        
    def showMenu(self):
        self.menu.show()

        self.animation = Animation.movingAnimation(
            Animation, self.menu, self.menuOpeningPos, 300
        )

        self.animation.start()

    def polygon(self):
        self.scene.clear()

        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        polygon = PolyGon(self.graphics)

        self.graphics.show()

    def update_my_styles(self, key, label):
        try:
            self.config[key] = int(label.text())
        except:
            self.config[key] = label.text()

        self.ecllipse.setBrush(QColor(self.config["color"]))

        self.ecllipse.setPen(
            QPen(QColor(self.config["outline"]), int(self.config["outline-width"]))
        )

        self.ecllipse.setRect(
            500, 500, int(self.config["radius"] * 2), int(self.config["radius"] * 2)
        )

    def continueToSave(self):
        self.graphics.hide()

        for x, y, width, height, color, outLine, radius in self.styles:

            self.draw.rounded_rectangle(
                (x, y, x + width, y + height), radius, color, outLine
            )

        self.image.save("new_image.png")

    def drawRect(self):
        inst = doodlerectItem(self.parent , self.renderArea , self.outParent)
        
        inst.createGraphics()
    
    def initLine(self, event):
        x = event.x() + self.graphics.horizontalScrollBar().value()

        y = event.y() + self.graphics.verticalScrollBar().value()

        pen = QPen(
            QColor(self.config["color"]),
            1,
            Qt.SolidLine,
            Qt.FlatCap,
            Qt.MiterJoin,
        )
        
        self.styles.append([x, y] + list(self.config.values()))

        self.tempStyles.append([x , y] + list(self.config.values()))

        self.rect = self.scene.addRect(x, y, 100, 500, pen)

        self.rect.setTransformOriginPoint(self.rect.boundingRect().topLeft())

        self.rect.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.rect.setFlag(QGraphicsItem.ItemIsMovable, True)

        self.rect.setFlag(QGraphicsItem.ItemIsFocusable, True)

        self.rect.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def floodImage(self):
        self.graphics.show()

        self.graphics.mousePressEvent = self.floodImageWithDim

        self.graphics.setCursor(Qt.CrossCursor)

    def floodImageWithDim(self, pos):        
        ImageDraw.floodfill(self.image, (pos.x(), pos.y()), (255, 0, 0 , 255))
        
        self.image.save("new_image.png")
        
        self.pixmap.setPixmap(QPixmap("new_image.png"))

    def rotateDraw(self, event: QMouseEvent):
        item_position = self.rect.transformOriginPoint()

        angle = (
            atan2(item_position.y() - event.y(), item_position.x() - event.x())
            / pi
            * 180
            - 45
        )

        self.rect.setRotation(angle)

    def removeMenu(self, startAni):
        self.animation = Animation.movingAnimation(
            Animation, self.menu, QPoint(2000, 0), 200
        )
        
        self.menu = QSliderMenu(self.parent)
        
        self.animation.finished.connect(self.menu.hide)

        self.animation.start()
        
        startAni.show()

    def manageMenu(self, startAni: QPushButton = None):
        stylesheet = """
            border: 1px solid #4C566A;
            padding: 10px;
            padding-left: 10px;
            color: white;
        """
        
        
        startAni.hide()
        
        self.menu.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        layout  = QHBoxLayout()
        
        widget = QCustomButton(text="" , window=None).create()
        
        widget.setStyleSheet(startAni.styleSheet())
        
        widget.setFixedSize(QSize(150 , 50))
        
        widget.clicked.connect(lambda : self.removeMenu(startAni))
                
        layout.addWidget(widget , alignment=Qt.AlignTop | Qt.AlignRight)
        
        self.menu.addMenu("" , layout , True)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)

        inputLabel.setPlaceholderText("Width")

        inputLabel.setStyleSheet(stylesheet)

        inputLabel.textChanged.connect(partial(self.update, "width", inputLabel))

        self.menu.addMenu("Width", inputLabel)

        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)

        inputLabel.setPlaceholderText("Height")

        inputLabel.setStyleSheet(stylesheet)

        inputLabel.textChanged.connect(partial(self.update, "height", inputLabel))

        self.menu.addMenu("Height", inputLabel)

        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)

        inputLabel.setPlaceholderText("Color")

        inputLabel.setStyleSheet(stylesheet)

        inputLabel.textChanged.connect(partial(self.update, "color", inputLabel))

        self.menu.addMenu("Color", inputLabel)

        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)

        inputLabel.setPlaceholderText("Outline")

        inputLabel.setStyleSheet(stylesheet)

        inputLabel.textChanged.connect(partial(self.update, "outline", inputLabel))

        self.menu.addMenu("Outline", inputLabel)

        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)

        inputLabel.setPlaceholderText("Outline Width")

        inputLabel.setStyleSheet(stylesheet)

        inputLabel.textChanged.connect(
            partial(self.update, "outline-width", inputLabel)
        )

        self.menu.addMenu("Outline Width", inputLabel)

        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)

        inputLabel.setPlaceholderText("Border Radius")

        inputLabel.setStyleSheet(stylesheet)

        inputLabel.textChanged.connect(
            partial(self.update, "border-radius", inputLabel)
        )

        self.menu.addMenu("Border Radius", inputLabel)

        self.menu.show()

        self.menu.move(QPoint(2000, 0))

        self.animation = Animation.movingAnimation(
            Animation, self.menu, QPoint(1900 - self.menu.width(), 0), 300
        )

        self.animation.start()


    def printOut(self):
        image = Image.open("GalleryMan/assets/processed_image.png").convert("RGBA")

        drawing = ImageDraw.ImageDraw(image)

        for (
            x,
            y,
            width,
            height,
            color,
            outlineColor,
            outlineWidth,
            border_radius,
        ) in self.styles.values():
            
            outlineWidth = 0 if int(outlineWidth) < 0 else int(outlineWidth)

            x, y, width, height = int(x), int(y), int(width), int(height)

            drawing.rounded_rectangle(
                (x, y, x + width, y + height),
                border_radius,
                color,
                outlineColor,
                outlineWidth,
            )

        image.save("GalleryMan/assets/processed_image.png")

        self.renderArea.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        self.animation = Animation.fadingAnimation(Animation, self.graphics, 300)

        self.animation.finished.connect(self.graphics.hide)

        self.animation.start()
