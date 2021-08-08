# Importing the modules
from GalleryMan.utils.imageDoodler import doodleImage
from GalleryMan.assets.cropper import ImageCropper
from GalleryMan.utils.infoFinder import getMoreInfo
from GalleryMan.utils.readers import getFontNameFromFile
import os
from GalleryMan.utils.doodleImage import PolyGon
from functools import partial, reduce
from math import atan2, e, pi
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtCore import (
    QAbstractAnimation,
    QLine,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSize,
    QStandardPaths,
    QVariant,
    QVariantAnimation,
    Qt,
    pyqtSlot,
)
from GalleryMan.assets.QEditorButtons import FilterView, PaletteView
from configparser import ConfigParser
from PyQt5.QtGui import (
    QColor,
    QCursor,
    QFont,
    QFontInfo,
    QFontMetrics,
    QImage,
    QKeySequence,
    QMouseEvent,
    QPaintDevice,
    QPainterPath,
    QPen,
    QPixmap,
    QTransform,
)
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsTextItem,
    QGraphicsView,
    QGraphicsWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QShortcut,
    QSizeGrip,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from GalleryMan.assets.QtHelpers import (
    Animation,
    PopUpMessage,
    QContinueButton,
    QCustomButton,
    QLayoutMaker,
    QSliderMenu,
    Thrower,
)
from json import loads
from GalleryMan.utils.helpers import *
from GalleryMan.utils.stickersArena import stickersViewer


class CustomLabel(QLabel):
    clicked = pyqtSignal(QPoint)

    def __init__(self, parent=None, listenFor=Qt.LeftButton):
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
    def __init__(
        self,
        parent: QApplication,
        application: QMainWindow,
        central: QWidget,
        config: ConfigParser,
        newParent: QScrollArea,
        out_widget,
    ) -> None:
        self.parent = parent

        self.application = application

        self.original = newParent.widget().layout()

        self.popup = PopUpMessage()

        self.config = config

        self.central = central

        self.animation = Animation.fadingAnimation(Animation, self.central, 200, True)

        self.animation.start()

        self.animation.finished.connect(self.central.show)

        self.newParent = newParent

        self.out_widget = out_widget

    def addtoLiked(self, directory_path, inst):
        self.heartWidget = inst.heartWidget

        icons = inst.iconStyles

        # with open("/home/strawhat54/.config/galleryman/data/likedPhotos.txt") as file:
        #     dirs = loads(file.read())
        dirs = []

        if directory_path in dirs:
            AddToLiked(self.application, directory_path, True).run()

            self.popup.new_msg(self.application, "Image Removed From Liked Images", 400)

            self.heartWidget.setStyleSheet(
                "color: {}; font-size: {}px; font-family: {}".format(
                    icons[0], icons[1], icons[2]
                )
            )

        else:

            AddToLiked(self.application, directory_path).run()

            self.popup.new_msg(self.application, "Image Added To Liked Images", 400)

            self.heartWidget.setStyleSheet(
                "color: {}; font-size: {}px; font-family: {}".format(
                    "#BF616A", icons[1], icons[2]
                )
            )

            Thrower(
                self.central.pos().x() + self.heartWidget.pos().x() + 50,
                self.central.pos().y() - self.heartWidget.pos().y() - 10,
                self.application,
            ).throw()

    def copyToClipboard(self, fileName):
        self.parent.clipboard().setPixmap(QPixmap(fileName))

    def showEditButtons(self, directory):
        def animation_callback():
            self.newParent.hide()

            new_label.setGeometry(self.newParent.takeWidget().geometry())

            new_label.setLayout(self.layout)

            self.newParent.setWidget(new_label)

            self.animation = Animation.fadingAnimation(
                Animation, self.central, 200, True
            )

            self.animation.start()

            self.animation.finished.connect(self.newParent.show)

        self.icons = loads(self.config.get("singleFolder", "editButtons-icons"))

        editButtons = ImageEditButtons(
            self,
            directory,
            self.application,
            self.newParent,
            self.config,
            self.out_widget,
        )

        self.functions = [
            editButtons.flipImage,
            editButtons.rotater,
            editButtons.cropImage,
            editButtons.filterImage,
            editButtons.stickerImage,
            editButtons.doodleImage,
            editButtons.addTextToImage,
            editButtons.imageAdjustment,
            lambda: self.swapLayout(self.original),
        ]

        self.layout = QLayoutMaker(self.icons, self.functions).make()

        editButtons.inst = self.layout

        new_label = QLabel()

        self.animation = Animation.fadingAnimation(Animation, self.central, 300)

        self.animation.start()

        self.animation.finished.connect(animation_callback)

    def swapLayout(self, layout):
        def animation_callback():
            self.newParent.hide()

            new_label.setGeometry(self.newParent.takeWidget().geometry())

            new_label.setLayout(layout)

            self.newParent.setWidget(new_label)

            self.animation = Animation.fadingAnimation(
                Animation, self.central, 200, True
            )

            self.animation.start()

            self.animation.finished.connect(self.newParent.show)

        new_label = QLabel()

        self.animation = Animation.fadingAnimation(Animation, self.central, 300)

        self.animation.start()

        self.animation.finished.connect(animation_callback)

    def moveToThrash(self, directory):
        os.replace(
            directory,
            "/home/strawhat54/.galleryman/data/thrashFiles/{}".format(
                directory[directory.rindex("/") + 1 :]
            ),
        )

        with open("/home/strawhat54/.galleryman/data/thrashLogs.txt", "r") as f:
            now = dict(loads(f.read()))

            now[
                "/home/strawhat54/.galleryman/data/thrashFiles/{}".format(
                    directory[directory.rindex("/") + 1 :]
                )
            ] = directory

        with open("/home/strawhat54/.galleryman/data/thrashLogs.txt", "w") as f:
            f.write(dumps(now))

        self.animation = QParallelAnimationGroup()

        self.animation.addAnimation(
            Animation.fadingAnimation(Animation, self.out_widget.parent(), 300)
        )

        self.animation.addAnimation(
            Animation.fadingAnimation(Animation, self.central, 300)
        )

        self.animation.start()

        self.animation.finished.connect(self.out_widget.hide)

        self.animation.finished.connect(self.central.hide)

        self.popup.new_msg(self.application, "Item Moved To Thrash", 500)

    def moreInfo(self, directory):
        self.icons = loads(self.config.get("singleFolder", "moreOptions-icons"))

        moreInfo = getMoreInfo(
            self.newParent, self.out_widget, directory, self.application
        )

        self.func = [
            moreInfo.castToScreen,
            moreInfo.getInfo,
            moreInfo.rename,
            moreInfo.searchGoogle,
            moreInfo.showInFullScreen,
            moreInfo.callback,
        ]

        self.layout = QLayoutMaker(self.icons, self.func).make()

        self.swapLayout(self.layout)


class ImageEditButtons:
    def __init__(
        self,
        inst,
        dir,
        parent: QMainWindow,
        outParent: QScrollArea,
        config: ConfigParser,
        renderArea: QRotateLabel,
    ) -> None:
        self.parent = parent

        self.dir = dir

        self.originalResponser = parent.resizeEvent

        self.inst = inst

        self.outParent = outParent

        self.renderArea = renderArea

        self.config = config

    def rotater(self):
        icons = loads(self.config.get("singleFolder", "editorCropper-icons"))

        self.sliderValue = QLineEdit()

        self.interiorFunctions = cropImage(
            self.dir, self.outParent, self.renderArea, self.sliderValue
        )

        func = [
            lambda: self.interiorFunctions.rotate90(),
            lambda: self.interiorFunctions.rotate90Right(),
            lambda: self.interiorFunctions.save(self.callback),
            lambda: self.callback(),
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
        self.sliderValue.setText("0")

        self.sliderValue.textChanged.connect(
            partial(self.rotateLabel, self.sliderValue.text())
        )

        self.slider.valueChanged.connect(self.rotateLabel)

        self.slider.setOrientation(Qt.Horizontal)

        self.sliderValue.setStyleSheet(
            """
            border-radius: 1px;
            border: 1px solid #4c566a;
            color: #d8dee9                         
        """
        )

        self.sliderValue.setFixedSize(QSize(200, 30))

        self.sliderValue.textChanged.connect(lambda: self.rotateLabel)

        childLayout.addWidget(self.slider)

        childLayout.addWidget(self.sliderValue)

        parentLayout.addLayout(childLayout)

        layout = QLayoutMaker(icons, func).make()

        parentLayout.addLayout(layout)

        self.swapLayout(parentLayout)

    def cropImage(self):
        cropper = ImageCropper(self, self.parent, None, self.renderArea, None)

        cropper.show()

    def filterImage(self):
        filters = FilterView(
            self.parent,
            self.renderArea,
            self.outParent,
            loads(self.config.get("singleFolder", "filters-colorIcons")),
            self.callback,
        )

        func = [
            lambda: filters.shady(),
            lambda: filters.sepia(),
            lambda: filters.cherry(),
            lambda: filters.underwater(),
            lambda: filters.purple(),
            lambda: filters.pink(),
            lambda: filters.dark(),
            lambda: filters.clear(),
            lambda: filters.realistic(),
            lambda: filters.cool_filter(),
            lambda: filters.remove_self(),
        ]

        layout = QLayoutMaker(
            loads(self.config.get("singleFolder", "filters-colorIcons")), func
        ).make()

        self.swapLayout(layout)

    def stickerImage(self):
        myStickers = stickersViewer(self.parent , self.renderArea, self.outParent)

        myStickers.initStock()

    def doodleImage(self):
        doodle = doodleImage(self.parent, self.renderArea, self.outParent)

        func = [
            lambda: doodle.freeHand(),
            lambda: doodle.drawRect(),
            lambda: doodle.line(),
            lambda: doodle.circle(),
            lambda: doodle.polygon(),
            lambda: doodle.floodImage(),
        ]

        icons = [
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
        ]

        layout = QLayoutMaker(icons, func).make()

        self.swapLayout(layout)

    def addTextToImage(self):
        textToImage = textInImage(self.parent, self.renderArea, self.outParent)

        textToImage.createGraphics()

    def imageAdjustment(self):
        icons = loads(self.config.get("singleFolder", "filter-icons"))

        view = PaletteView(
            None,
            "GalleryMan/assets/processed_image.png",
            self.renderArea,
            self.config,
            lambda: print("NONE"),
            
            
        )

        func = [
            lambda: view.blur(),
            lambda: view.sharp(),
            lambda: view.increaseBrightness(),
            lambda: view.increaseContrast(),
            lambda: view.increaseExposure(),
            lambda: print("LOLCAT"),
        ]

        layout = QLayoutMaker(icons, func).make()

        self.swapLayout(layout)

    def flipImage(self):
        flipper = imageFlipper(self.renderArea, self.outParent)

        func = [
            lambda: flipper.flipLeft(),
            lambda: flipper.flipTop(),
            lambda: self.callback(),
        ]

        icons = loads(self.config.get("singleFolder", "editroFlipper-icons"))

        layout = QLayoutMaker(icons, func).make()

        self.swapLayout(layout)

    def swapLayout(self, layout):
        self.central = self.outParent.parent()

        def animation_callback():
            self.outParent.hide()

            new_label.setGeometry(self.outParent.takeWidget().geometry())

            new_label.setLayout(layout)

            self.outParent.setWidget(new_label)

            self.animation = Animation.fadingAnimation(
                Animation, self.central, 200, True
            )

            self.animation.start()

            self.animation.finished.connect(self.outParent.show)

        new_label = QLabel()

        self.animation = Animation.fadingAnimation(Animation, self.outParent.widget(), 500)

        self.animation.finished.connect(animation_callback)

        self.animation.start()

    def callback(self):
        self.icons = loads(self.config.get("singleFolder", "editButtons-icons"))

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
            self.callback,
        ]

        self.layout = QLayoutMaker(self.icons, self.functions).make()

        self.new_label = QLabel()

        self.new_label.setGeometry(self.outParent.takeWidget().geometry())

        self.new_label.setLayout(self.layout)

        self.outParent.setWidget(self.new_label)

        self.swapLayout(self.layout)

    def rotateLabel(self, value=None):
        value = int(
            self.sliderValue.text()
            if value not in [None, ""]
            else self.sliderValue.text()
        )

        self.interiorFunctions.degree = 90 * self.interiorFunctions.rotations

        self.sliderValue.textChanged.disconnect()

        self.sliderValue.setText(str(self.interiorFunctions.degree % 360))

        self.sliderValue.textChanged.connect(self.rotateLabel)

        self.slider.setValue(value)

        self.renderArea.start_animation(self.interiorFunctions.degree)


class cropImage:
    SAVE_DIR = "GalleryMan/assets/processed_image.png"

    def __init__(
        self, dir: str, newParent, renderArea: QRotateLabel, outDisplay
    ) -> None:
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

    def swapLayout(self, layout):
        self.central = self.newParent.parent()

        def animation_callback():
            self.newParent.hide()

            new_label.setGeometry(self.newParent.takeWidget().geometry())

            new_label.setLayout(layout)

            self.newParent.setWidget(new_label)

            self.animation = Animation.fadingAnimation(
                Animation, self.central, 200, True
            )

            self.animation.start()

            self.animation.finished.connect(self.newParent.show)

        new_label = QLabel()

        self.animation = Animation.fadingAnimation(Animation, self.central, 300)

        self.animation.start()

        self.animation.finished.connect(animation_callback)

    def save(self, callback):
        image = Image.open("GalleryMan/assets/processed_image.png")

        image = image.rotate(-(self.degree % 360), expand=1, fillcolor=(255, 0, 0, 1))

        image.save("GalleryMan/assets/processed_image.png")

        callback()


class textInImage:
    def __init__(self, parent, out_widget, scrollArea) -> None:
        self.parent = parent

        self.out_widget = out_widget

        self.scrollArea = scrollArea

        self.layouts = []

        self.stylesheet = ""

        self.graphics = QGraphicsView(self.parent)

        self.graphics.resizeEvent = self.responser

        self.graphics.show()

        self.storedValue = {
            "color": "#88C0D0",
            "font-family": "Comfortaa",
            "font-size": 11,
        }

        self.menu = QSliderMenu(self.graphics)

        startAni = QCustomButton("AAA", self.graphics).create()

        startAni.setGeometry(QRect(1800, 10, 100, 100))

        startAni.clicked.connect(lambda: self.manageMenu())

        startAni.show()

        self.current = 0

    def updateStyling(self, newValue):
            
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.label.setText(self.storedValue["text"])
        
        self.resizeToContent(self.label.text())
        
        self.label.setStyleSheet(
            """
            color: {};
            background-color: transparent;
            font-size: {}px;
            font-family: {};
        """.format(
                self.storedValue["color"],
                self.storedValue["font-size"],
                self.storedValue["font-family"],
            )
        )
        
        pass

    def swapLayout(self, layout):
        self.central = self.scrollArea.parent()

        def animation_callback():
            self.scrollArea.hide()

            new_label.setGeometry(self.scrollArea.takeWidget().geometry())

            new_label.setLayout(layout)

            self.scrollArea.setWidget(new_label)

            self.animation = Animation.fadingAnimation(
                Animation, self.central, 200, True
            )

            self.animation.start()

            self.animation.finished.connect(self.scrollArea.show)

        new_label = QLabel()

        self.animation = Animation.fadingAnimation(Animation, self.central, 300)

        self.animation.start()

        self.animation.finished.connect(animation_callback)

    def update(self, property, label):
        self.storedValue[property] = label.text()

        self.updateStyling(None)

    def createGraphics(self):
        self.scene = QGraphicsScene()

        self.graphics.setGeometry(QRect(0, 0, 1980, 1080))

        self.graphics.setScene(self.scene)

        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        self.graphics.show()

        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # self.label = DraggableInput(self.graphics)
        
        # self.label.show()
    
        # self.label.setStyleSheet("background-color: transparent; font-family: Comfortaa; font-size: 30px")

        # self.label.textChanged.connect(self.resizeToContent)

        # self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.label = DraggableLabel(None)
        
        self.label.setText("Your Text")
        
        self.label.setStyleSheet("""
            background-color: transparent;
            font-size: 40px;
            font-family: Comfortaa                         
        """)
        
        self.label.move(QPoint(100 , 100))

        self.scene.addWidget(self.label)
        
        self.label.show()

        continueButton = QCustomButton("Continue", self.graphics).create()

        continueButton.clicked.connect(lambda: self.saveText())

        continueButton.setGeometry(QRect(0, 0, 500, 100))

        continueButton.show()

    def resizeToContent(self, text):
        font = QFont(
            self.storedValue["font-family"], int(self.storedValue["font-size"])
        )

        met = QFontMetrics(font)

        width = met.width(text)

        height = met.height()

        self.label.setText(text)

        self.label.setFixedSize(width, height)
        
        print(width , height , text)

        self.label.adjustSize()

    def saveText(self):
        
        def callback():
            self.graphics.hide()
            
            self.out_widget.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))
            
        self.image = Image.open("GalleryMan/assets/processed_image.png")
        
        area = self.graphics.geometry()
                
        image = QImage(area.size(), QImage.Format_ARGB32_Premultiplied)
        
        painter = QPainter(image)
        
        self.scene.render(painter, QRectF(image.rect()), QRectF(area))
        
        painter.end()
        
        image.save("GalleryMan/assets/processed_image.png")
        
        self.animation = Animation.fadingAnimation(Animation , self.graphics , 200)
        
        self.animation.finished.connect(callback)
        
        self.animation.start()

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

        inputLabel.textChanged.connect(partial(self.update, "width", inputLabel))

        self.menu.addMenu("Width", inputLabel)
        
        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        inputLabel.setPlaceholderText("Text")
        
        inputLabel.setText("Your Text")

        inputLabel.setStyleSheet(stylesheet)

        inputLabel.textChanged.connect(partial(self.update, "text", inputLabel))

        self.menu.addMenu("Text", inputLabel)

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

        inputLabel.setPlaceholderText("Font Family")

        inputLabel.setStyleSheet(stylesheet)

        inputLabel.textChanged.connect(partial(self.update, "font-family", inputLabel))

        self.menu.addMenu("Font Family", inputLabel)

        inputLabel = QLineEdit()

        inputLabel.setAlignment(Qt.AlignLeft)

        inputLabel.setPlaceholderText("Font Size")

        inputLabel.setStyleSheet(stylesheet)

        inputLabel.textChanged.connect(partial(self.update, "font-size", inputLabel))

        self.menu.addMenu("Font Size", inputLabel)

        self.menu.show()

        self.menu.move(QPoint(2000, 0))

        self.animation = Animation.movingAnimation(
            Animation, self.menu, QPoint(1900 - self.menu.width(), 0), 300
        )

        self.animation.start()

    def responser(self, event: QResizeEvent):
        print(event.size())

class imageEraser:
    def __init__(self, parent) -> None:
        self.parent = parent

        self.image = Image.open("GalleryMan/assets/processed_image.png")

        self.menu = QSliderMenu(self.parent)

        self.values = {"width": 15, "height": 15}

        self.graphics = QGraphicsView(self.parent)

        self.start = QCustomButton("S", self.graphics).create()

        self.start.clicked.connect(lambda: self.manageMenu())

        self.start.setGeometry(QRect(1000, 200, 100, 100))

        self.start.show()

    def createEraser(self):

        self.scene = QGraphicsScene()

        self.graphics.setScene(self.scene)

        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.graphics.show()

        self.graphics.setGeometry(QRect(0, 0, 1980, 1080))

        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        self.graphics.mouseMoveEvent = self.mouseHandler

    def mouseHandler(self, event):
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

        self.menu.move(QPoint(2000, 0))

        self.animation = Animation.movingAnimation(
            Animation, self.menu, QPoint(1900 - self.menu.width(), 0), 300
        )

        self.animation.start()

    def update(self, key, label):
        self.values[key] = label.text()


class imageFlipper:
    def __init__(self, renderArea, outParent) -> None:
        self.renderArea = renderArea

        self.outParent = outParent

        self.image = Image.open("GalleryMan/assets/processed_image.png")

    def flipLeft(self):
        def animation_callback():
            new_image = self.image.transpose(method=Image.FLIP_LEFT_RIGHT)

            self.renderArea.set_pixmap(self.createPixmap(new_image))

            new_image.save("GalleryMan/assets/processed_image.png")

            self.image = Image.open("GalleryMan/assets/processed_image.png")

            self.animation = Animation.fadingAnimation(
                Animation, self.renderArea, 200, True, startValue=0.5
            )

            self.animation.start()

        self.animation = Animation.fadingAnimation(
            Animation, self.renderArea, 200, endValue=0.5
        )

        self.animation.start()

        self.animation.finished.connect(animation_callback)

    def flipTop(self):
        def animation_callback():
            new_image = self.image.transpose(method=Image.FLIP_TOP_BOTTOM)

            self.renderArea.set_pixmap(self.createPixmap(new_image))

            new_image.save("GalleryMan/assets/processed_image.png")

            self.image = Image.open("GalleryMan/assets/processed_image.png")

            self.animation = Animation.fadingAnimation(
                Animation, self.renderArea, 200, True, startValue=0.5
            )

            self.animation.start()

        self.animation = Animation.fadingAnimation(
            Animation, self.renderArea, 200, endValue=0.5
        )

        self.animation.start()

        self.animation.finished.connect(animation_callback)

    def createPixmap(self, image):
        if image.mode == "RGB":
            r, g, b = image.split()
            image = Image.merge("RGB", (b, g, r))

        elif image.mode == "RGBA":
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
    def __init__(self, parent, outArea) -> None:
        self.parent = parent
        self.outArea = outArea

    def sendLayout(self) -> QHBoxLayout:
        with open(
            "/home/strawhat54/.config/galleryman/data/recentStickers.txt", "r"
        ) as f:
            data = loads(f.read())

        layout = QHBoxLayout()

        for i in data:
            preview = CustomLabel()

            preview.setFixedWidth(200)

            preview.setFixedHeight(100)

            preview.setScaledContents(True)

            preview.clicked.connect(partial(self.useSticker, i))

            preview.setPixmap(QPixmap(i))

            layout.addWidget(preview)

        return layout

    def useSticker(self, dir):
        self.graphics = QGraphicsView()

        self.graphics.setGeometry(QRect(0, 0, 1980, 1080))

        self.scene = QGraphicsScene()

        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        self.graphics.setScene(self.scene)

        imageAdder = DraggableLabel(self.graphics)

        self.graphics.setWindowFlags(Qt.SubWindow)

        layout = QHBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QSizeGrip(self.graphics), 0, Qt.AlignLeft | Qt.AlignTop)

        layout.addWidget(QSizeGrip(self.graphics), 0, Qt.AlignRight | Qt.AlignBottom)

        imageAdder.setGeometry(100, 100, 400, 400)

        imageAdder.setPixmap(QPixmap(dir))

        imageAdder.setScaledContents(True)

        imageAdder.show()

        imageAdder.setLayout(layout)

        self.graphics.show()


