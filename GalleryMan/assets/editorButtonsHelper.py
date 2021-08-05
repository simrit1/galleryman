# Importing the modules
from GalleryMan.assets.cropper import ImageCropper
from GalleryMan.utils.infoFinder import getMoreInfo
from GalleryMan.utils.readers import getFontNameFromFile
import os
from GalleryMan.utils.doodleImage import PolyGon
from functools import partial
from math import atan2, pi
from PIL import Image , ImageDraw , ImageFont
from PyQt5.QtCore import QAbstractAnimation, QLine, QParallelAnimationGroup, QPoint, QPropertyAnimation, QRect, QRectF, QSize, QStandardPaths, QVariant, QVariantAnimation, Qt, pyqtSlot
from GalleryMan.assets.QEditorButtons import FilterView, PaletteView
from configparser import ConfigParser
from PyQt5.QtGui import QColor, QCursor, QFont, QFontInfo, QFontMetrics, QImage, QMouseEvent, QPaintDevice, QPainterPath, QPen, QPixmap, QTransform
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsScene, QGraphicsSimpleTextItem, QGraphicsView, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QScrollArea, QSizeGrip, QSlider, QVBoxLayout, QWidget
from GalleryMan.assets.QtHelpers import Animation, PopUpMessage, QContinueButton, QCustomButton, QLayoutMaker, QSliderMenu, Thrower
from json import loads
from GalleryMan.utils.helpers import *

class CustomLabel(QLabel):
    clicked = pyqtSignal(QPoint)

    def __init__(self, parent=None , listenFor = Qt.LeftButton):
        super().__init__(parent=parent)
        
        self.listenFor = listenFor

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == self.listenFor:
            self.clicked.emit(event.pos())
            
            self.eventPos = event.pos()
            
class QRotateLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(QRotateLabel, self).__init__(*args, **kwargs)
        self._pixmap = QPixmap()

        self.curr = 0

        self.initial = 0

        self.init_ani()

    def init_ani(self):
        self._animation = QVariantAnimation(
            self,
            startValue=self.initial,
            endValue=self.curr,
            duration=100,
            valueChanged=self.on_valueChanged,
        )

        self.initial = self.curr

    def set_pixmap(self, pixmap):
        self._pixmap = pixmap
        self.setPixmap(self._pixmap)

    def start_animation(self, deg):
        if self._animation.state() != QAbstractAnimation.Running:
            self.curr, self.initial = deg, self.curr

            self.init_ani()

            self._animation.start()

    def get_curr_deg(self):
        return self.curr % 360

    @pyqtSlot(QVariant)
    def on_valueChanged(self, value):
        t = QTransform()
        t.rotate(value)
        self.setPixmap(self._pixmap.transformed(t))



class QEditorHelper:
    def __init__(self , parent: QApplication , application: QMainWindow , central: QWidget , config: ConfigParser, newParent: QScrollArea , out_widget) -> None:
        self.parent = parent
        
        self.application = application
        
        self.original = newParent.widget().layout()
        
        self.popup = PopUpMessage()
        
        self.config = config
        
        self.central = central
        
        self.animation = Animation.fadingAnimation(Animation , self.central , 200 , True)
        
        self.animation.start()
        
        self.animation.finished.connect(self.central.show)
        
        self.newParent = newParent
        
        self.out_widget = out_widget
    
    def addtoLiked(self , directory_path , inst):
        self.heartWidget = inst.heartWidget
        
        icons = inst.iconStyles
        
        with open("/home/strawhat54/.config/galleryman/data/likedPhotos.txt") as file:
            dirs = loads(file.read())
                    
        if(directory_path in dirs):
            AddToLiked(self.application , directory_path , True).run()
            
            self.popup.new_msg(self.application , "Image Removed From Liked Images" , 400)
            
            self.heartWidget.setStyleSheet(
                "color: {}; font-size: {}px; font-family: {}".format(
                    icons[0] , icons[1], icons[2]
                )
            )
            
            
        else:
            
            AddToLiked(self.application , directory_path).run()
                    
            self.popup.new_msg(self.application , "Image Added To Liked Images" , 400)
            
            self.heartWidget.setStyleSheet(
                "color: {}; font-size: {}px; font-family: {}".format(
                    "#BF616A", icons[1], icons[2]
                )
            )
            
            Thrower(self.central.pos().x() + self.heartWidget.pos().x() + 50, self.central.pos().y() - self.heartWidget.pos().y() - 10, self.application).throw()
            
    
    def copyToClipboard(self , fileName):        
        self.parent.clipboard().setPixmap(QPixmap(fileName))
    
    def showEditButtons(self , directory):
        def animation_callback():            
            self.newParent.hide()
            
            new_label.setGeometry(self.newParent.takeWidget().geometry())
            
            new_label.setLayout(self.layout)
            
            self.newParent.setWidget(new_label)
            
            self.animation = Animation.fadingAnimation(Animation , self.central , 200 , True)
            
            self.animation.start()
            
            self.animation.finished.connect(self.newParent.show)
        
        self.icons = loads(self.config.get("singleFolder" , "editButtons-icons"))
        
        editButtons = ImageEditButtons(self , directory , self.application, self.newParent , self.config , self.out_widget)
        
        self.functions = [
            editButtons.flipImage,
            editButtons.rotater,
            editButtons.cropImage,
            editButtons.filterImage,
            editButtons.stickerImage,
            editButtons.doodleImage,
            editButtons.addTextToImage,
            editButtons.imageAdjustment,
            lambda : self.swapLayout(self.original)
        ]
                
        self.layout = QLayoutMaker(self.icons , self.functions).make()
        
        editButtons.inst = self.layout
                        
        new_label = QLabel()
                
        self.animation = Animation.fadingAnimation(Animation , self.central , 300)
        
        self.animation.start()
        
        self.animation.finished.connect(animation_callback)
                
    def swapLayout(self , layout):
        def animation_callback():            
            self.newParent.hide()
            
            new_label.setGeometry(self.newParent.takeWidget().geometry())
            
            new_label.setLayout(layout)
            
            self.newParent.setWidget(new_label)
            
            self.animation = Animation.fadingAnimation(Animation , self.central , 200 , True)
            
            self.animation.start()
            
            self.animation.finished.connect(self.newParent.show)
            
        new_label = QLabel()
                
        self.animation = Animation.fadingAnimation(Animation , self.central , 300)
        
        self.animation.start()
        
        self.animation.finished.connect(animation_callback)
        
    def moveToThrash(self , directory):        
        os.replace(directory , "/home/strawhat54/.galleryman/data/thrashFiles/{}".format(directory[directory.rindex("/") + 1:]))
        
        with open('/home/strawhat54/.galleryman/data/thrashLogs.txt' , 'r') as f:
            now = dict(loads(f.read()))
            
            now["/home/strawhat54/.galleryman/data/thrashFiles/{}".format(directory[directory.rindex("/") + 1:])] = directory
            
        with open('/home/strawhat54/.galleryman/data/thrashLogs.txt' , 'w') as f:
            f.write(dumps(now))
        
        self.animation = QParallelAnimationGroup()
        
        self.animation.addAnimation(Animation.fadingAnimation(Animation , self.out_widget.parent() , 300))
        
        self.animation.addAnimation(Animation.fadingAnimation(Animation , self.central , 300))
        
        self.animation.start()
        
        self.animation.finished.connect(self.out_widget.hide)
        
        self.animation.finished.connect(self.central.hide)
        
        self.popup.new_msg(self.application , "Item Moved To Thrash" , 500)
        
    def moreInfo(self , directory):
        self.icons = loads(self.config.get("singleFolder" , "moreOptions-icons"))
        
        moreInfo = getMoreInfo(self.newParent , self.out_widget , directory , self.application)
        
        self.func = [
            moreInfo.castToScreen,
            moreInfo.getInfo,
            moreInfo.rename,
            moreInfo.searchGoogle,
            moreInfo.showInFullScreen,
            moreInfo.callback
        ]
        
        self.layout = QLayoutMaker(self.icons , self.func).make()
        
        self.swapLayout(self.layout)
        
        
        
class ImageEditButtons:
    def __init__(self , inst , dir , parent: QMainWindow , outParent: QScrollArea , config: ConfigParser , renderArea: QRotateLabel) -> None:
        self.parent = parent
        
        self.dir = dir
        
        self.originalResponser = parent.resizeEvent
        
        self.inst = inst
        
        self.outParent = outParent
        
        self.renderArea = renderArea
        
        self.config = config
    
    def rotater(self):        
        icons = loads(self.config.get("singleFolder" , "editorCropper-icons"))
        
        self.sliderValue = QLineEdit()
        
        self.interiorFunctions = cropImage(self.dir , self.outParent , self.renderArea , self.sliderValue)
        
        func = [
            lambda : self.interiorFunctions.rotate90(),
            lambda : self.interiorFunctions.rotate90Right(),
            lambda : self.interiorFunctions.save(self.callback),
            lambda : self.callback()
        ]
        
        parentLayout = QVBoxLayout()
        
        childLayout = QHBoxLayout()
        
        self.slider = QSlider(self.outParent)
        
        self.slider.setMaximum(360)
        
        self.slider.setMinimum(0)
        
        self.slider.setStyleSheet(
            """
            QSlider::groove:horizontal{{
                background-color: {};
                border-radius: {}px; 
                border: {}px solid {}     
            }}
            QSlider::handle:horizontal{{
                width: {}px;
                height: {}px;
                color: {};
                border-radius: {}px;
                border: {}px solid {};
            }}
            """.format(
                self.config.get("singleFolder", "slider-backgroundColor"),
                self.config.get("singleFolder", "slider-borderRadius"),
                self.config.get("singleFolder", "slider-borderWidth"),
                self.config.get("singleFolder", "slider-borderColor"),
                self.config.get("singleFolder", "slider-holderWidth"),
                self.config.get("singleFolder", "slider-holderHeight"),
                self.config.get("singleFolder", "slider-holderColor"),
                self.config.get("singleFolder", "slider-holderRadius"),
                self.config.get("singleFolder", "slider-holderBorderWidth"),
                self.config.get("singleFolder", "slider-holderColor"),
            )
        )
        self.sliderValue.setText('0')
        
        self.sliderValue.textChanged.connect(partial(self.rotateLabel , self.sliderValue.text()))
        
        self.slider.valueChanged.connect(self.rotateLabel)
        
        self.slider.setOrientation(Qt.Horizontal)
        
        self.sliderValue.setStyleSheet("""
            border-radius: 1px;
            border: 1px solid #4c566a;
            color: #d8dee9                         
        """)
        
        self.sliderValue.setFixedSize(QSize(200 , 30))
        
        self.sliderValue.textChanged.connect(lambda : self.rotateLabel)
        
        childLayout.addWidget(self.slider)
        
        childLayout.addWidget(self.sliderValue)
        
        parentLayout.addLayout(childLayout)
        
        layout = QLayoutMaker(icons , func).make()
        
        parentLayout.addLayout(layout)
                
        self.swapLayout(parentLayout)
        
    def cropImage(self):
        cropper = ImageCropper(self , self.parent , None , None , None)
        
        cropper.show()
    
    def filterImage(self):
        filters = FilterView(self.parent , self.renderArea , self.outParent , loads(self.config.get("singleFolder" , "filters-colorIcons")) , self.callback)
        
        func = [
            lambda : filters.shady(),
            lambda : filters.sepia(),
            lambda : filters.cherry(),
            lambda : filters.underwater(),
            lambda : filters.purple(),
            lambda : filters.pink(),
            lambda : filters.dark(),
            lambda : filters.clear(),
            lambda : filters.realistic(),
            lambda : filters.cool_filter(),
            lambda : filters.remove_self()
        ]
                
        layout = QLayoutMaker(loads(self.config.get("singleFolder" , "filters-colorIcons")) , func).make()
                
        self.swapLayout(layout)
    
    def stickerImage(self):
        myStickers = stickerImage(self.renderArea , self.outParent)
        
        layout = myStickers.sendLayout()
        
        self.swapLayout(layout)
    
    def doodleImage(self):
        doodle = doodleImage(self.parent , self.renderArea , self.outParent)
        
        func = [
            lambda : doodle.freeHand(),
            lambda : doodle.drawRect(),
            lambda : doodle.line(),
            lambda : doodle.circle(),
            lambda : doodle.polygon(),
            lambda : doodle.floodImage()
        ]
        
        icons = [
            [" " , "#88C0D0" , 40 , "SauceCodePro Nerd Font"],
            [" " , "#88C0D0" , 40 , "SauceCodePro Nerd Font"],
            [" " , "#88C0D0" , 40 , "SauceCodePro Nerd Font"],
            [" " , "#88C0D0" , 40 , "SauceCodePro Nerd Font"],
            [" " , "#88C0D0" , 40 , "SauceCodePro Nerd Font"],
            [" " , "#88C0D0" , 40 , "SauceCodePro Nerd Font"]
        ]
        
        layout = QLayoutMaker(icons , func).make()
        
        self.swapLayout(layout)
        
    def addTextToImage(self):
        textToImage = textInImage(self.parent , self.renderArea , self.outParent)
        
        textToImage.createGraphics()
    
    def imageAdjustment(self):
        icons = loads(self.config.get("singleFolder" , 'filter-icons'))
        
        view = PaletteView(None , "GalleryMan/assets/processed_image.png" , self.renderArea , self.config , lambda : print("NONE"))
        
        func = [
            lambda : view.blur(),
            lambda : view.sharp(),
            lambda : view.increaseBrightness(),
            lambda : view.increaseContrast(),
            lambda : view.increaseExposure(),
            lambda : print("LOLCAT")
        ]
        
        layout = QLayoutMaker(icons , func).make()
        
        self.swapLayout(layout)
    
    def flipImage(self):
        flipper = imageFlipper(self.renderArea , self.outParent)
        
        func = [
            lambda : flipper.flipLeft(),
            lambda : flipper.flipTop(),
            lambda : self.callback()
        ]
        
        icons = loads(self.config.get("singleFolder" , "editroFlipper-icons"))
        
        layout = QLayoutMaker(icons , func).make()
        
        self.swapLayout(layout)

    
    def swapLayout(self , layout):
        self.central = self.outParent.parent()
        
        def animation_callback():     
                   
            self.outParent.hide()
            
            new_label.setGeometry(self.outParent.takeWidget().geometry())
            
            new_label.setLayout(layout)
            
            self.outParent.setWidget(new_label)
            
            self.animation = Animation.fadingAnimation(Animation , self.central , 200 , True)
            
            self.animation.start()
            
            self.animation.finished.connect(self.outParent.show)
            
        new_label = QLabel()
                
        self.animation = Animation.fadingAnimation(Animation , self.central , 300)
        
        self.animation.finished.connect(animation_callback)
        
        self.animation.start()
        
        
    def callback(self):
        self.icons = loads(self.config.get("singleFolder" , "editButtons-icons"))
        
        self.renderArea.setPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
                
        self.functions = [
            self.flipImage,
            self.rotater,
            self.cropImage,
            self.filterImage,
            self.stickerImage,
            self.doodleImage,
            self.addTextToImage,
            self.imageAdjustment,
            self.callback
        ]
        
        self.layout = QLayoutMaker(self.icons , self.functions).make()
                                
        self.new_label = QLabel()
        
        self.new_label.setGeometry(self.outParent.takeWidget().geometry())
                
        self.new_label.setLayout(self.layout)
        
        self.outParent.setWidget(self.new_label)
        
        self.swapLayout(self.layout)
    
    def rotateLabel(self , value=None):
        value = int(self.sliderValue.text() if value not in [None , ""] else self.sliderValue.text())
                                
        self.interiorFunctions.degree = 90 * self.interiorFunctions.rotations
        
        self.sliderValue.textChanged.disconnect()
        
        self.sliderValue.setText(str(self.interiorFunctions.degree % 360))
            
        self.sliderValue.textChanged.connect(self.rotateLabel)    
        
        self.slider.setValue(value)
        
        self.renderArea.start_animation(self.interiorFunctions.degree)
            
class cropImage:
    SAVE_DIR = "GalleryMan/assets/processed_image.png"
    
    def __init__(self , dir: str , newParent , renderArea: QRotateLabel , outDisplay) -> None:
        self.directory = dir
        self.image = Image.open(self.directory)
        self.outDisplay = outDisplay
        self.renderArea = renderArea
        self.rotations = 0
        self.degree = 0
        self.newParent = newParent
        
    
    def rotate90(self):
        self.degree += 90
        
        self.rotations += 1
        
        self.outDisplay.setText(str(self.degree % 360))
                
        self.renderArea.start_animation(self.degree % 360)
        
        self.updateImage()
    
    def rotate90Right(self):
        self.degree -= 90
        
        self.rotations -= 1
        
        self.outDisplay.setText(str(self.degree % 360))
                
        self.renderArea.start_animation(self.degree % 360)
        
        self.updateImage()
    
    def updateImage(self):
        self.image = Image.open("GalleryMan/assets/processed_image.png")
        
    def swapLayout(self , layout):
        self.central = self.newParent.parent()
        
        def animation_callback():            
            self.newParent.hide()
            
            new_label.setGeometry(self.newParent.takeWidget().geometry())
            
            new_label.setLayout(layout)
            
            self.newParent.setWidget(new_label)
            
            self.animation = Animation.fadingAnimation(Animation , self.central , 200 , True)
            
            self.animation.start()
            
            self.animation.finished.connect(self.newParent.show)
            
        new_label = QLabel()
                
        self.animation = Animation.fadingAnimation(Animation , self.central , 300)
        
        self.animation.start()
        
        self.animation.finished.connect(animation_callback)
    
    def save(self , callback):
        image = Image.open("GalleryMan/assets/processed_image.png") 
        
        image = image.rotate(-(self.degree % 360) , expand=1 , fillcolor=(255 , 0 , 0 , 1))
        
        image.save("GalleryMan/assets/processed_image.png")
        
        callback()
        
class textInImage:
    def __init__(self , parent , out_widget , scrollArea) -> None:
        self.parent = parent
        
        self.out_widget = out_widget
        
        self.scrollArea = scrollArea
        
        self.layouts = []
                
        self.stylesheet = ""
            
        self.graphics = QGraphicsView(self.parent)
        
        self.graphics.resizeEvent = self.responser
            
        self.graphics.show()
        
        self.storedValue = {
            "width": 300,
            "height": 100,
            "color": "#88C0D0",
            "font-family": "Comfortaa",
            "font-size": 11
        }
        
        self.menu = QSliderMenu(self.parent)
        
        startAni = QCustomButton("AAA" , self.graphics).create()
        
        startAni.setGeometry(QRect(
            1800, 10 , 100 , 100
        ))
        
        startAni.clicked.connect(lambda : self.manageMenu())
        
        startAni.show()
        
        self.current = 0

    def updateStyling(self , newValue):
        self.label.setFixedSize(QSize(int(self.storedValue["width"]) , int(self.storedValue["height"])))
        
        self.label.setStyleSheet("""
            color: {};
            background-color: transparent;
            font-size: {}px;
            font-family: {};
        """.format(
            self.storedValue["color"],
            self.storedValue["font-size"],
            self.storedValue["font-family"],
        ))
    
    def swapLayout(self , layout):
        self.central = self.scrollArea.parent()
        
        def animation_callback():            
            self.scrollArea.hide()
            
            new_label.setGeometry(self.scrollArea.takeWidget().geometry())
            
            new_label.setLayout(layout)
            
            self.scrollArea.setWidget(new_label)
            
            self.animation = Animation.fadingAnimation(Animation , self.central , 200 , True)
            
            self.animation.start()
            
            self.animation.finished.connect(self.scrollArea.show)
            
        new_label = QLabel()
                
        self.animation = Animation.fadingAnimation(Animation , self.central , 300)
        
        self.animation.start()
        
        self.animation.finished.connect(animation_callback)
        
        
    def update(self , property , label):
        self.storedValue[property] = label.text()
        
        self.updateStyling(None)
        
        # self.resizeToContent(self.label.text())
        
    def createGraphics(self):                
        self.scene = QGraphicsScene()
        
        self.graphics.setGeometry(QRect(0 , 0 , 1980 , 1080))
        
        self.graphics.setScene(self.scene)
        
        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
    
        
        self.graphics.show()
        
        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.label = QGraphicsSimpleTextItem("LOLCAT")
        
        self.label.setPen(QPen(QColor("#88C0D0") , 100))
        
        self.label.setFlag(QGraphicsItem.ItemIsMovable)
        
        self.label.setPos(100 , 100)
        
        self.scene.addItem(self.label)
        
        self.label.show()
        
        # self.label.setStyleSheet("background-color: transparent; font-family: Comfortaa; font-size: 30px")
        
        # # self.label.textChanged.connect(self.resizeToContent)
            
        # self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # self.label.move(QPoint(100 , 100))
        
        continueButton = QCustomButton('Continue' , self.parent).create()
        
        continueButton.clicked.connect(lambda : self.saveText())
        
        continueButton.setGeometry(QRect(0 , 0 , 500 , 100))        
        
        continueButton.show()
        
    def resizeToContent(self , text):        
        font = QFont(self.storedValue["font-family"] , int(self.storedValue["font-size"]))
        
        print(font.family() , font.pointSize())
        
        met = QFontMetrics(font)
        
        width = met.width(text)

        height = met.height()
        
        self.label.setText(text)
        
        self.label.setFixedSize(width , height)
        
        # self.label.adjustSize()
        
    def saveText(self):
        
        self.image = Image.open("GalleryMan/assets/processed_image.png")
                
        font_paths = QStandardPaths.standardLocations(QStandardPaths.FontsLocation)
                        
        draw = ImageDraw.ImageDraw(self.image)
        
        x , y = self.label.x() + self.graphics.horizontalScrollBar().value() , self.label.y() + self.graphics.verticalScrollBar().value() + 20
        
        font = ImageFont.truetype("/home/strawhat54/.fonts/Comfortaa-Regular.ttf" , int(self.storedValue["font-size"]))
        
        draw.text((x, y), self.label.text(), font = font, fill="#2E3440")

        self.image.save("MYFILE.png")
    
        
    def manageMenu(self):
        stylesheet = """
            border: 1px solid #4C566A;
            padding: 10px;
            padding-left: 10px;
            color: white;
        """
        
        self.menu.show()
        
        self.menu.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        inputLabel.setPlaceholderText("Width")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "width" , inputLabel))
        
        self.menu.addMenu("Width" , inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Height")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "height" , inputLabel))
        
        self.menu.addMenu("Height" , inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Color")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "color" , inputLabel))
        
        self.menu.addMenu("Color" , inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Font Family")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "font-family" , inputLabel))
        
        self.menu.addMenu("Font Family" , inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Font Size")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "font-size" , inputLabel))
        
        self.menu.addMenu("Font Size" , inputLabel)
        
        self.menu.show()
        
        self.menu.move(QPoint(2000 , 0))
                
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1900 - self.menu.width() , 0) , 300)
        
        self.animation.start()
        
    def responser(self , event: QResizeEvent):
        print(event.size())
        
        
class doodleImage:
    def __init__(self , parent , renderArea , outParent) -> None:
        self.parent = parent
        
        self.renderArea = renderArea 
        
        self.outParent = outParent
        
        self.pressed = False
        
        self.image = Image.open("GalleryMan/assets/processed_image.png")
        
        self.draw = ImageDraw.ImageDraw(self.image)
        
        self.graphics = QGraphicsView(self.parent)
        
        self.parent.resizeEvent = self.responser
        
        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.styles =  []
                
        self.scene = QGraphicsScene(self.parent)
        
        self.graphics.setScene(self.scene)
        
        self.continueNext = QContinueButton(self.graphics).start()
        
        self.continueNext.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
            background-color: transparent
        """)
        
        self.continueNext.enterEvent(None)
        
        self.continueNext.leaveEvent(None)
        
        self.continueNext.clicked.connect(lambda : self.printOut())
        
        self.continueNext.setGeometry(QRect(100 , 100 , 500 , 100))
            
        self.continueNext.show()
        
        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        self.graphics.setGeometry(QRect(0 , 0 , 1980 , 1080))
        
        self.config = {
            "width": 2,
            "height": 2,
            "color": "#88C0D0",
            "outline": "#2E3440",
            "border-radius": 10
        }

    def freeHand(self):
        self.config = {
            "width": 2,
            "height": 2,
            "color": "#88C0D0",
            "outline": "#2E3440",
            "outline-width": 1,
            "border-radius": 0
        }
        
        self.continueNext.move(QPoint(
            self.parent.width() - self.continueNext.width() + 300,
            self.parent.height() - self.continueNext.height()
        ))
        
        self.scene.clear()
        
        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        self.menu = QSliderMenu(self.parent)
        
        self.startAni = QCustomButton(" " , self.parent).create()
        
        self.startAni.setGeometry(QRect(
            1770, 5 , 100 , 100
        ))
        
        self.startAni.setStyleSheet("border: 0; background-color: transparent; float: left")
        
        self.startAni.clicked.connect(partial(self.manageMenu , self.startAni))
        
        self.startAni.show()
        
        self.graphics.show()
                
        self.graphics.mousePressEvent = lambda event : self.mouseHandler(event , "pressEvent")
        
        self.graphics.mouseMoveEvent = lambda event : self.mouseHandler(event , "moveEvent")
        
        self.graphics.mouseReleaseEvent = self._reset
        
    def _reset(self , _):
        self.pressed = False
        
    def mouseHandler(self , event: QMouseEvent , type):   
        if(type == "pressEvent"):
            self.pressed = True
        else:
            if(not self.pressed): return
             
        if(event.x() < 0 or event.y() < 0):
            return
        
        x = event.x() + self.graphics.horizontalScrollBar().value()
        
        y = event.y() + self.graphics.verticalScrollBar().value()
                
        pen = QPen(
            QColor(self.config["outline"]),
            1,
            Qt.SolidLine,
            Qt.FlatCap,
            Qt.MiterJoin,
        )
        
        pen.setWidth(int(self.config["outline-width"]))
        
        print(self.config)
        
        self.styles.append([x , y] + list(self.config.values()))
        
        path = QPainterPath()
        
        path.addRoundedRect(QRectF(x , y, int(self.config["width"]) , int(self.config["height"])) , int(self.config["border-radius"]) , int(self.config["border-radius"]))
                
        rect = self.scene.addPath(path , pen)
            
        rect.setBrush(QColor(self.config["color"]))
        
    def line(self):
        self.scene.clear()
        
        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))  
        
        pen = QPen()
        
        pen.setColor(QColor("#88C0D0"))
        
        pen.setStyle(Qt.SolidLine)
        
        self.lineRect = self.scene.addLine(500 , 500 , 700 , 700 , pen)
        
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
            "color": "#88C0D0"
        }
        
        for name , propertyName in zip(["Start Position" , 'End Position' , "Color" , "Width" ] , ["start-position" , 'end-position' , "color" , "width"]):
            inputBox = QClickableTextEdit()
            
            inputBox.setProperty("class" , propertyName)
            
            if(name in ["Start Position" , "End Position"]):
                inputBox.setPlaceholderText("Click To Choose")
                
                inputBox.clicked.connect(partial(self.askForPos , inputBox))
                
            else:
                inputBox.setPlaceholderText(name)
            
            inputBox.setFixedHeight(50)

            inputBox.setStyleSheet(stylesheet)
            
            inputBox.textChanged.connect(partial(self.update , propertyName , inputBox))
            
            self.menu.addMenu(name , inputBox)
            
        self.graphics.show()
        
        self.menu.show()
                            
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1870 - self.menu.width() , 0) , 300)
                
        self.animation.start()
    
    def askForPos(self , inputt: QLineEdit , cordinates: QPoint):
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(2000 , 0) , 300)
        
        self.animation.start()
                
        self.outerLabel = QLabel(self.graphics)
        
        self.outerLabel.setGeometry(self.graphics.geometry())
        
        self.outerLabel.setText("Click on the point")
        
        self.outerLabel.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        self.outerLabel.show()
        
        self.outerLabel.setStyleSheet("font-size: 30px; background-color: #2E344050")
        
        self.graphics.setCursor(Qt.CrossCursor)
        
        self.outerLabel.mousePressEvent = lambda pos: self.setPos(pos , inputt)
    
    def setPos(self , pos , inputt: QLineEdit):
        inputt.setText("{} x {}".format(pos.x() , pos.y()))
        
        self.outerLabel.hide()
        
        classS = inputt.property("class")
                
        if(classS == "start-position"):    
            self.lineRect.setLine(pos.x() + self.graphics.horizontalScrollBar().value() , pos.y() + self.graphics.verticalScrollBar().value() , self.lineRect.line().x2()  , self.lineRect.line().y2())
        else:
            self.lineRect.setLine(self.lineRect.line().x1() , self.lineRect.line().y1() , pos.x() + self.graphics.horizontalScrollBar().value(), pos.y() + self.graphics.verticalScrollBar().value())
                    
        self.update(inputt.property("class") , inputt)
        
        self.graphics.setCursor(Qt.ArrowCursor)        
        
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1870 - self.menu.width() , 0) , 300)
        
        self.animation.start()
        
    def updateStylings(self):      
        pen = QPen(QColor(self.config["color"]) , int(self.config["width"]) , Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        
        try:
            self.lineRect.setPen(pen)
        except:
            pass
        
    def circle(self):
        def responser(event: QResizeEvent):
            self.continueNext.move(QPoint(
                event.size().width() - self.continueNext.width() + 50,
                event.size().height() - self.continueNext.height()
            ))
            
            button.move(QPoint(
                event.size().width() - button.width(),
                button.y()
            ))
            
            if(not self.menu.pos() == self.originalPos):    
                self.menuOpeningPos = QPoint(
                    event.size().width() - self.menu.width(),
                    0
                )
                
                button.click()
            
        self.menu = QSliderMenu(self.parent)
        
        self.menuOpeningPos = QPoint(
            1870 - self.menu.width(),
            0
        )
        
        self.originalPos = QPoint(2000 , 0)
        
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
        
        self.continueNext.clicked.disconnect()
        
        self.continueNext.clicked.connect(self.drawCircleOnImage)
        
        self.pen = QPen(QColor(self.config["outline-color"]) , 10 , Qt.SolidLine)
        
        self.ecllipse = self.scene.addEllipse(500 , 500 , self.config["radius"] * 2 , self.config["radius"] * 2 , self.pen)
        
        self.ecllipse.setFlag(QGraphicsItem.ItemIsMovable)
        
        self.ecllipse.setBrush(QColor(self.config["color"]))
        
        for name , propertyName in zip(["Radius" , "Color" , "Outline" , "Outline Width"] , ["radius" , "color" , "outline" , "outline-width"]):
            inputBox = QClickableTextEdit()
            
            inputBox.setProperty("class" , propertyName)

            inputBox.setPlaceholderText(name)
            
            inputBox.setFixedHeight(50)

            inputBox.setStyleSheet(stylesheet)
            
            inputBox.textChanged.connect(partial(self.update_my_styles , propertyName , inputBox))
            
            self.menu.addMenu(name , inputBox)
            
        self.parent.resizeEvent = responser
            
        self.graphics.show()
        
        button = QCustomButton("S" , self.parent).create()
        
        button.setGeometry(QRect(
            self.parent.width() - 100,
            0,
            100,
            100    
        ))
        
        button.show()
        
        button.clicked.connect(self.showMenu)
        
        self.menu.move(self.originalPos)
        
    def drawCircleOnImage(self):
        self.image = Image.open("GalleryMan/assets/processed_image.png")
        
        draw = ImageDraw.ImageDraw(self.image)
        
        draw.ellipse(
            self.ecllipse.pos().x() + int(self.config["radius"],
            self.ecllipse.pos().y() , self.ecllipse.pos().x() + int(self.config["radius"]) + int(self.config["radius"]) , 
            self.ecllipse.pos().y() + int(self.config["radius"])) , self.config["color"] ,
            self.config["outline-color"] , int(self.config["outline-width"]))
            
        self.image.save("GalleryMan/assets/processed_image.png")
        
    
    def showMenu(self):            
        self.menu.show()
                
        self.animation = Animation.movingAnimation(Animation , self.menu , self.menuOpeningPos , 300)
        
        self.animation.start()
        
    
    def polygon(self):
        self.scene.clear()
        
        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        polygon = PolyGon(self.graphics)
                
        self.graphics.show()
    
    def update_my_styles(self , key , label):        
        try:
            self.config[key] = int(label.text())
        except:
            self.config[key] = label.text()
                    
        self.ecllipse.setBrush(QColor(self.config["color"]))
        
        self.ecllipse.setPen(QPen(QColor(self.config["outline"]) , int(self.config["outline-width"])))
                
        self.ecllipse.setRect(500 , 500 , int(self.config["radius"] * 2) , int(self.config["radius"] * 2))        

    def continueToSave(self):
        self.graphics.hide()
        print("color")
        

        for x , y , width , height , color , outLine , radius in self.styles:
            
            self.draw.rounded_rectangle((x , y, x + width , y + height) , radius , color , outLine)
            
        
        self.image.save("new_image.png")
        
    def drawRect(self):
        self.config = {
            "background-color": "#2E3440",
            "border-color": "#2E3440",
            "border-width": 40,
            "border-radius": 0
        }
        
        def updateConfig(label: QLineEdit):
            Sclass = label.property("class")
            
            self.config[Sclass] = label.text()
            
            self.rectangle.setStyleSheet("""
                QLabel{{
                    background-color: {color};
                    border: {width}px solid {colorB};
                    border-radius: {rad}     
                }}
                
                QSizeGrip{{
                    background-color: {color};
                }}
            """.format(
                color=self.config["background-color"],
                width=self.config["border-width"],
                colorB=self.config["border-color"],
                rad=self.config["border-radius"]
            ))
        
        self.rectangle = QGripLabel()
        
        self.scene.addWidget(self.rectangle)
        
        self.rectangle.setGeometry(QRect(100 , 100 , 500 , 500))
        
        self.rectangle.show()
        
        self.graphics.show()
        
        self.menu = QSliderMenu(self.graphics)
        
        self.continueNext.clicked.disconnect()
        
        self.continueNext.clicked.connect(partial(self.drawRectOnImage , self.rectangle))
        
        for name , specialClass in zip(["Background Color" , "Border Color" , "Border Width" , "Border Radius"] , ["background-color" , "border-color" , "border-width" , "border-radius"]):
            box = QLineEdit()
            
            box.setPlaceholderText(name)
            
            box.setProperty("class" , specialClass)
            
            box.setFixedHeight(50)
            
            box.textChanged.connect(partial(updateConfig , box))
            
            self.menu.addMenu(name , box)
            
        def callback():
            self.menu.show()
            
            self.menu.move(QPoint(2000 , 0))
                    
            self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1900 - self.menu.width() , 0) , 300)
            
            self.animation.start()
        
        startAni = QCustomButton(" " , self.graphics).create()
        
        startAni.setGeometry(QRect(1700 , 0 , 100 , 100))
        
        startAni.setStyleSheet("""
            background-color: transparent;
            color: #88C0D0;
        """)
        
        startAni.show()
        
        startAni.clicked.connect(callback)
            
    def drawRectOnImage(self , label: QGripLabel):
        self.image = Image.open("GalleryMan/assets/processed_image.png").convert("RGBA")
        
        draw = ImageDraw.ImageDraw(self.image)
        
        draw.rounded_rectangle((label.geometry().x() , label.geometry().y() , label.geometry().x() + label.geometry().width() , label.geometry().y() + label.geometry().height()), int(self.config["border-radius"] ), self.config["background-color"] , self.config["border-color"] , int(self.config["border-width"]))
        
        self.image.save("new_image.png")
    
    def initLine(self , event):
        x = event.x() + self.graphics.horizontalScrollBar().value()
        
        y = event.y() + self.graphics.verticalScrollBar().value()
                
        pen = QPen(
            QColor(self.config["color"]),
            1,
            Qt.SolidLine,
            Qt.FlatCap,
            Qt.MiterJoin,
        )
        
        print(self.config)
                
        self.styles.append([x , y] + list(self.config.values()))
                
        self.rect = self.scene.addRect(x , y , 100 , 500 , pen)
        
        self.rect.setTransformOriginPoint(self.rect.boundingRect().topLeft())
        
        self.rect.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
        self.rect.setFlag(QGraphicsItem.ItemIsMovable, True)
        
        self.rect.setFlag(QGraphicsItem.ItemIsFocusable, True)
        
        self.rect.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
    def floodImage(self):
        self.graphics.show()
        
        cursor = QCursor(QPixmap("painter.png").scaled(50 , 50 , transformMode=Qt.SmoothTransformation))
        
        self.graphics.mousePressEvent = self.floodImageWithDim
    
        self.graphics.setCursor(cursor)
        
    def floodImageWithDim(self , pos):
        flood = ImageDraw.floodfill(self.image , (pos.x() , pos.y()) , (255 , 0 , 0 , 255))
        
        self.image.save("new_image.png")
    
    def rotateDraw(self , event: QMouseEvent):  
        item_position = self.rect.transformOriginPoint()
        
        angle = (
            atan2(item_position.y() - event.y(), item_position.x() - event.x())
            / pi
            * 180
            - 45
        )
            
        self.rect.setRotation(angle)
        
    def removeMenu(self , startAni):
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(2000 , 0) , 200)
        
        self.animation.start()
        
        self.menu.hide()
        
        self.menu = QSliderMenu(self.parent)
        
        startAni.setText(" ")
        
        startAni.clicked.disconnect()
        
        startAni.clicked.connect(partial(self.manageMenu , startAni))
        
    def manageMenu(self , startAni: QPushButton = None):
        stylesheet = """
            border: 1px solid #4C566A;
            padding: 10px;
            padding-left: 10px;
            color: white;
        """
        
        startAni.setText("")
        
        startAni.clicked.disconnect()
        
        startAni.clicked.connect(partial(self.removeMenu , startAni))
        
        startAni.setParent(self.parent)
        
        startAni.show()
                
        self.menu.setAlignment(Qt.AlignTop | Qt.AlignRight)

        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Width")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "width" , inputLabel))
        
        self.menu.addMenu("Width" , inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Height")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "height" , inputLabel))
        
        self.menu.addMenu("Height" , inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Color")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "color" , inputLabel))
        
        self.menu.addMenu("Color" , inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Outline")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "outline" , inputLabel))
        
        self.menu.addMenu("Outline" , inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Outline Width")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "outline-width" , inputLabel))
        
        self.menu.addMenu("Outline Width" , inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Border Radius")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "border-radius" , inputLabel))
        
        self.menu.addMenu("Border Radius" , inputLabel)
        
        self.menu.show()
        
        self.menu.move(QPoint(2000 , 0))
                
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1900 - self.menu.width() , 0) , 300)
        
        self.animation.start()
        
    def update(self , key , input: QLineEdit):
        value = input.text()
        
        self.config[key] = value
        
        self.updateStylings()
        
    def printOut(self):
        image = Image.open("GalleryMan/assets/processed_image.png").convert("RGBA")
        
        drawing = ImageDraw.ImageDraw(image)
        
        for x , y , width , height , color , outlineColor , outlineWidth , border_radius in self.styles:
            outlineWidth = 0 if outlineWidth < 0 else outlineWidth
            
            x , y , width , height = int(x) , int(y) , int(width) , int(height)
                        
            drawing.rounded_rectangle(
                (x , y , x + width , y + height), border_radius , color , outlineColor , outlineWidth
            )
            
        image.save("GalleryMan/assets/processed_image.png")
        
        self.renderArea.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        self.animation = Animation.fadingAnimation(Animation , self.graphics , 300)
        
        self.animation.finished.connect(self.graphics.hide)
        
        self.animation.start()
        
    def responser(self , event: QResizeEvent):
        self.startAni.move(QPoint(
            event.size().width() - self.startAni.width() - 30,
            self.startAni.y(),
        ))

        self.continueNext.move(QPoint(
            event.size().width() - self.startAni.width() - 90,
            event.size().height() - self.startAni.height(),
        ))
            
class imageEraser:
    def __init__(self , parent) -> None:
        self.parent = parent
        
        self.image = Image.open("GalleryMan/assets/processed_image.png")
        
        self.menu = QSliderMenu(self.parent)
        
        self.values = {
            "width": 15,
            "height": 15
        }
        
        self.graphics = QGraphicsView(self.parent)
        
        self.start = QCustomButton("S" , self.graphics).create()
        
        self.start.clicked.connect(lambda : self.manageMenu())
        
        self.start.setGeometry(QRect(1000 , 200 , 100 , 100))
        
        self.start.show()
    
    def createEraser(self):
        
        self.scene = QGraphicsScene()
        
        self.graphics.setScene(self.scene)
        
        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.graphics.show()
        
        self.graphics.setGeometry(QRect(0 , 0 , 1980 , 1080))
        
        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        self.graphics.mouseMoveEvent = self.mouseHandler
            
    def mouseHandler(self , event):
        pass
        
    def manageMenu(self):
        stylesheet = """
            border: 1px solid #4C566A;
            padding: 10px;
            padding-left: 10px;
            color: white;
        """
        
        self.menu.show()
            
        self.menu.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Width")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "width" , inputLabel))
        
        self.menu.addMenu("Width" , inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Height")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "height" , inputLabel))
        
        self.menu.addMenu("Height" , inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)
        
        inputLabel.setPlaceholderText("Color")
        
        inputLabel.setStyleSheet(stylesheet)
        
        inputLabel.textChanged.connect(partial(self.update , "color" , inputLabel))
        
        self.menu.addMenu("Color" , inputLabel)
        
        self.menu.move(QPoint(2000 , 0))
                
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1900 - self.menu.width() , 0) , 300)
        
        self.animation.start()
        
    def update(self , key , label):
        self.values[key] = label.text()

class imageFlipper:
    def __init__(self , renderArea , outParent) -> None:
        self.renderArea = renderArea
        
        self.outParent = outParent
        
        self.image = Image.open("GalleryMan/assets/processed_image.png")
    
    def flipLeft(self):
        def animation_callback():
            new_image = self.image.transpose(method=Image.FLIP_LEFT_RIGHT)
        
            self.renderArea.set_pixmap(self.createPixmap(new_image))
                    
            new_image.save("GalleryMan/assets/processed_image.png")
            
            self.image = Image.open("GalleryMan/assets/processed_image.png")
            
            self.animation = Animation.fadingAnimation(Animation , self.renderArea , 200 , True , startValue=0.5)
            
            self.animation.start()
        
        self.animation = Animation.fadingAnimation(Animation , self.renderArea , 200 , endValue=0.5)
        
        self.animation.start()
        
        self.animation.finished.connect(animation_callback)
        
        
    def flipTop(self):
        def animation_callback():
            new_image = self.image.transpose(method=Image.FLIP_TOP_BOTTOM)
        
            self.renderArea.set_pixmap(self.createPixmap(new_image))
                    
            new_image.save("GalleryMan/assets/processed_image.png")
            
            self.image = Image.open("GalleryMan/assets/processed_image.png")
            
            self.animation = Animation.fadingAnimation(Animation , self.renderArea , 200 , True , startValue=0.5)
            
            self.animation.start()
        
        self.animation = Animation.fadingAnimation(Animation , self.renderArea , 200 , endValue=0.5)
        
        self.animation.start()
        
        self.animation.finished.connect(animation_callback)
        
    def createPixmap(self , image):
        if image.mode == "RGB":
            r, g, b = image.split()
            image = Image.merge("RGB", (b, g, r))
            
        elif  image.mode == "RGBA":
            r, g, b, a = image.split()
            image = Image.merge("RGBA", (b, g, r, a))
            
        elif image.mode == "L":
            image = image.convert("RGBA")

        im2 = image.convert("RGBA")
        
        data = im2.tobytes("raw", "RGBA")
        
        qim = QImage(data, image.size[0], image.size[1], QImage.Format_ARGB32)
        
        pixmap = QPixmap.fromImage(qim)
        
        return pixmap
    
class stickerImage:
    def __init__(self , parent , outArea) -> None:
        self.parent = parent 
        self.outArea = outArea
        
    def sendLayout(self) -> QHBoxLayout:
        with open("/home/strawhat54/.config/galleryman/data/recentStickers.txt" , "r") as f:
            data = loads(f.read())
        
        layout = QHBoxLayout()
        
        for i in data:
            preview = CustomLabel()
            
            preview.setFixedWidth(200)
            
            preview.setFixedHeight(100)
            
            preview.setScaledContents(True)
            
            preview.clicked.connect(partial(self.useSticker , i))
            
            preview.setPixmap(QPixmap(i))
            
            layout.addWidget(preview)
            
        return layout
    
    def useSticker(self , dir):        
        self.graphics = QGraphicsView()
        
        self.graphics.setGeometry(QRect(0 , 0 , 1980 , 1080))
        
        self.scene = QGraphicsScene()
        
        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        self.graphics.setScene(self.scene)
        
        imageAdder = DraggableLabel(self.graphics)
        
        self.graphics.setWindowFlags(Qt.SubWindow)
        
        layout = QHBoxLayout()
        
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(
        
            QSizeGrip(self.graphics), 0,
        
            Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(
        
            QSizeGrip(self.graphics), 0,
        
            Qt.AlignRight | Qt.AlignBottom)
        
        imageAdder.setGeometry(100 , 100 , 400 , 400)
        
        imageAdder.setPixmap(QPixmap(dir))
        
        imageAdder.setScaledContents(True)
        
        imageAdder.show()
        
        imageAdder.setLayout(layout)
        
        self.graphics.show()