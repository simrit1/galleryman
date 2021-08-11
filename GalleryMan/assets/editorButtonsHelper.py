# Importing the modules
from GalleryMan.utils.imageDoodler import doodleImage
from GalleryMan.assets.cropper import ImageCropper
from GalleryMan.utils.infoFinder import getMoreInfo
import os
from functools import partial
from PIL import Image
from PyQt5.QtCore import (
    QAbstractAnimation,
    QParallelAnimationGroup,
    QPoint,
    QRect,
    QRectF,
    QSize,
    QVariant,
    QVariantAnimation,
    Qt,
    pyqtSlot,
)
from GalleryMan.assets.QEditorButtons import FilterView, PaletteView
from configparser import ConfigParser
from PyQt5.QtGui import (
    QFont,
    QFontMetrics,
    QImage,
    QMouseEvent,
    QPixmap,
    QTransform,
)
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QScrollArea,
    QSizeGrip,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from GalleryMan.assets.QtHelpers import (
    Animation,
    PopUpMessage,
    QCustomButton,
    QLayoutMaker,
    QSliderMenu,
    Thrower,
)
from json import loads
from GalleryMan.utils.helpers import *
from GalleryMan.utils.stickersArena import stickersViewer


class CustomLabel(QLabel):
    """A Custom, Clickable Label"""
    clicked = pyqtSignal(QPoint)

    def __init__(self, parent=None, listenFor=Qt.LeftButton):
        super().__init__(parent=parent)
        
        # Make the listenFor variable global
        self.listenFor = listenFor

    def mouseReleaseEvent(self, event: QMouseEvent):
        
        # Check for the mouse release event
        if event.button() == self.listenFor:
            
            # Emit the clicked function
            self.clicked.emit(event.pos())
    
            self.eventPos = event.pos()

class QRotateLabel(QLabel):
    """A Custom, Rotatable `QLabel`"""
    
    def __init__(self, *args, **kwargs):
        super(QRotateLabel, self).__init__(*args, **kwargs)
        
        # Make the pixmap global
        self._pixmap = QPixmap()
        
        # A variable to store current rotation
        self.curr = 0
        
        # Initial degree
        self.initial = 0
        
        # Init animation
        self.init_ani()

    def init_ani(self):
        
        # Create a animation
        self._animation = QVariantAnimation(
            self,
            startValue=self.initial,
            endValue=self.curr,
            duration=100,
            valueChanged=self.on_valueChanged,
        )
        
        # Set the initial value with the current degree
        self.initial = self.curr

    def set_pixmap(self, pixmap):
        
        # Change the pixmap
        self._pixmap = pixmap

        # Set the pixmap
        self.setPixmap(self._pixmap)

    def start_animation(self, deg):
        # Check if animation isn't running
        if self._animation.state() != QAbstractAnimation.Running:
            
            # Swap the degrees
            self.curr, self.initial = deg, self.curr
            
            # Create a animation with new degree
            self.init_ani()
            
            # Start the animation
            self._animation.start()

    def get_curr_deg(self):
        return self.curr % 360

    @pyqtSlot(QVariant)
    def on_valueChanged(self, value):
        t = QTransform()
        t.rotate(value)
        self.setPixmap(self._pixmap.transformed(t))


class QEditorHelper:
    LIKED_FOLDERS = "/home/strawhat54/.galleryman/data/likedFolders.txt"
    
    def __init__(
        self,
        parent: QApplication,
        application: QMainWindow,
        central: QWidget,
        config: ConfigParser,
        newParent: QScrollArea,
        out_widget,
    ) -> None:
        
        # Make every args global
        self.parent = parent

        self.application = application

        self.original = newParent.widget().layout()

        self.newParent = newParent

        self.out_widget = out_widget

        self.config = config

        self.central = central

        # Make a popup mmessage instance
        self.popup = PopUpMessage()
        
        # Hide the scrollArea to switch the buttons with the new buttons
        self.animation = Animation.fadingAnimation(Animation, self.central, 200, True)
        
        # Start the animation
        self.animation.start()
        
        # Again show the scroll area when finished
        self.animation.finished.connect(self.central.show)

    def addtoLiked(self, directory_path, inst):
        
        # Get the heart widget
        self.heartWidget = inst.heartWidget
        
        # Get the icons
        icons = inst.iconStyles
        
        # Read all the currently liked photos
        with open(self.LIKED_FOLDERS) as file:
            dirs = loads(file.read())
            
        # Check if the directory that will be added to liked is already there or not
        if directory_path in dirs:
            
            # Remove it from liked if it is already thete
            AddToLiked(self.application, directory_path, True).run()
            
            # Show a new message
            self.popup.new_msg(self.application, "Image Removed From Liked Images", 400)
            
            # Change its color
            self.heartWidget.setStyleSheet(
                "color: {}; font-size: {}px; font-family: {}".format(
                    icons[0], icons[1], icons[2]
                )
            )

        else:
            
            # Add to liked 
            AddToLiked(self.application, directory_path).run()
            
            # New message
            self.popup.new_msg(self.application, "Image Added To Liked Images", 400)
            
            # Chnage colors
            self.heartWidget.setStyleSheet(
                "color: {}; font-size: {}px; font-family: {}".format(
                    "#BF616A", icons[1], icons[2]
                )
            )
            
            # Throw some hearts on click
            Thrower(
                self.central.pos().x() + self.heartWidget.pos().x() + 50,
                self.central.pos().y() - self.heartWidget.pos().y() - 10,
                self.application,
            ).throw()

    def copyToClipboard(self, fileName):
        # Add the image to the application's clipboard
        self.parent.clipboard().setPixmap(QPixmap(fileName))

    def showEditButtons(self, directory):
        
        # Callback when animation is over
        def animation_callback():
            
            # Hide the scrollArea and change the buttons while it is hidden
            self.newParent.hide()

            new_label.setGeometry(self.newParent.takeWidget().geometry())

            new_label.setLayout(self.layout)

            self.newParent.setWidget(new_label)
            
            # Show the scrollArea
            self.animation = Animation.fadingAnimation(
                Animation, self.central, 200, True
            )

            self.animation.start()

            self.animation.finished.connect(self.newParent.show)
            
        # Get the preffered icons
        self.icons = loads(self.config.get("singleFolder", "editButtons-icons"))
        
        # Create an instance of the handler of this layout
        editButtons = ImageEditButtons(
            self,
            directory,
            self.application,
            self.newParent,
            self.config,
            self.out_widget,
        )
        
        # Make a layout from the buttons and function
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
        
        # Change the layout
        editButtons.inst = self.layout
        
        # Animate 
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
        
        # Relace the directory to the app's trash folder
        try:
            os.replace(
                directory,
                "/home/strawhat54/.galleryman/data/thrashFiles/{}".format(
                    directory[directory.rindex("/") + 1 :]
                ),
            )
        except:
            print("IMAGE NOT FOUND!")
        
        # Now open the trash file logs and add a entry
        with open("/home/strawhat54/.galleryman/data/thrashLogs.txt", "r") as f:
            now = dict(loads(f.read()))

            now[
                "/home/strawhat54/.galleryman/data/thrashFiles/{}".format(
                    directory[directory.rindex("/") + 1 :]
                )
            ] = directory
        
        # Write the updated information
        with open("/home/strawhat54/.galleryman/data/thrashLogs.txt", "w") as f:
            f.write(dumps(now))
            
        # Animate
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
        
        # Add a new message when its completed
        self.popup.new_msg(self.application, "Item Moved To Thrash", 500)

    def moreInfo(self, directory):
        # Get preferred icons
        self.icons = loads(self.config.get("singleFolder", "moreOptions-icons"))
        
        # Create an instance of the handdler
        moreInfo = getMoreInfo(
            self.newParent, self.out_widget, directory, self.application
        )
        
        # Merge the buttons with the function
        self.func = [
            moreInfo.getInfo,
            moreInfo.rename,
            moreInfo.showInFullScreen,
            moreInfo.callback,
        ]
        
        # Make the layout and swap
        self.layout = QLayoutMaker(self.icons, self.func).make()

        self.swapLayout(self.layout)
        
    def closeWithSave(self , directory):
        dialog = QDialog(self.application)
        
        buttonsLayout = QHBoxLayout()
        
        save = QCustomButton("Save and Close" , None).create()
        
        save.setStyleSheet("""
            color: #FFF;
            font-size: 20px                   
        """)
        
        buttonsLayout.addWidget(save , alignment=Qt.AlignLeft)
        
        sep = QLabel(text="|")
        
        buttonsLayout.addWidget(sep , alignment=Qt.AlignCenter)
        
        discard = QCustomButton("Discard and Close" , None).create()
        
        discard.setStyleSheet("""
            color: #FFF;
            font-size: 20px                   
        """)
        
        buttonsLayout.addWidget(discard , Qt.AlignRight)
        
        dialog.setLayout(buttonsLayout)
        
        dialog.setFixedSize(400 , 50)
        
        dialog.exec_()


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
        
        # Make all the args global
        self.parent = parent

        self.dir = dir

        self.originalResponser = parent.resizeEvent

        self.inst = inst

        self.outParent = outParent

        self.renderArea = renderArea

        self.config = config

    def rotater(self):
        # Get the preffered icons
        icons = loads(self.config.get("singleFolder", "editorRotater-icons"))
        
        # A input box to show the current degree
        self.sliderValue = QLineEdit()
        
        # Make an intsance of the handler function
        self.interiorFunctions = cropImage(
            self.dir, self.outParent, self.renderArea, self.sliderValue
        )
        
        # Make a layout
        func = [
            lambda: self.interiorFunctions.rotate90(),
            lambda: self.interiorFunctions.rotate90Right(),
            lambda: self.interiorFunctions.save(self.callback),
            lambda: self.callback(),
        ]

        parentLayout = QVBoxLayout()

        childLayout = QHBoxLayout()
        
        # Add the slider to layout
        self.slider = QSlider(self.outParent)
        
        # Set fixed maximum and minimum values
        self.slider.setMaximum(360)

        self.slider.setMinimum(0)
        
        self.slider.valueChanged.connect(self.rotateLabel)
        
        # Some Stylings
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
        
        # set the value to 0 for first time
        self.sliderValue.setText("0")
        
        # Rotate the label when the text is changed
        self.sliderValue.textChanged.connect(self.rotateLabel)
        
        # Set orientation
        self.slider.setOrientation(Qt.Horizontal)
        
        # Stylings
        self.sliderValue.setStyleSheet(
            """
            border-radius: {}px;
            border: {}px solid {};
            color: {};
            background-color: {}                       
        """.format(
            self.config.get("singleFolder" , "input-borderRadius"),
            self.config.get("singleFolder" , "input-borderWidth"),
            self.config.get("singleFolder" , "input-borderColor"),
            self.config.get("singleFolder" , "input-textColor"),
            self.config.get("singleFolder" , "input-backgroundColor"),
        ))
        
        # Fixed size
        self.sliderValue.setFixedSize(QSize(
            int(self.config.get("singleFolder" , "input-width")),
            int(self.config.get("singleFolder" , "input-height"))    
        ))
        
        # Rotate label when slider is changed
        self.sliderValue.textChanged.connect(lambda: self.rotateLabel)
        
        # Add to layouts
        childLayout.addWidget(self.slider)

        childLayout.addWidget(self.sliderValue)

        parentLayout.addLayout(childLayout)
        
        # Make layout
        layout = QLayoutMaker(icons, func).make()
        
        # Swap layout
        parentLayout.addLayout(layout)

        self.swapLayout(parentLayout)

    def cropImage(self):
        
        # Initate the cropper class
        cropper = ImageCropper(self.parent, self.renderArea , self.config)
        
        # Show the cropper
        cropper.show()

    def filterImage(self):
        
        # Initate the filter class
        filters = FilterView(
            self.parent,
            self.renderArea,
            self.outParent,
            loads(self.config.get("singleFolder", "filters-colorIcons")),
            self.callback,
        )
        
        # Functions and make a layout
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
        
        # Swap layout
        self.swapLayout(layout)

    def stickerImage(self):
        # Create a sticker viewer instance
        myStickers = stickersViewer(self.parent , self.renderArea, self.outParent)
        
        # Show the stock
        myStickers.initStock()

    def doodleImage(self):
        
        # Initate the class
        doodle = doodleImage(self.parent, self.renderArea, self.outParent)
        
        # get all the respective functions
        func = [
            lambda: doodle.freeHand(),
            lambda: doodle.drawRect(),
            lambda: doodle.line(),
            lambda: doodle.circle(),
            lambda: doodle.polygon(),
            lambda: doodle.floodImage(),
        ]
        
        # Get the preffered icons
        icons = [
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
            [" ", "#88C0D0", 40, "SauceCodePro Nerd Font"],
        ]
        
        # Make the layout and swap
        layout = QLayoutMaker(icons, func).make()

        self.swapLayout(layout)

    def addTextToImage(self):
        # Initate the text in image class
        textToImage = textInImage(self.parent, self.renderArea, self.outParent)
        
        # Create the graphics
        textToImage.createGraphics()

    def imageAdjustment(self):
        # Get the preffered icons
        icons = loads(self.config.get("singleFolder", "filter-icons"))
        
        # Initate the handler class 
        view = PaletteView(
            None,
            "GalleryMan/assets/processed_image.png",
            self.renderArea,
            self.config,
            lambda: print("NONE"),
        )
        
        # Get respective functions and make layout
        func = [
            lambda: view.blur(),
            lambda: view.sharp(),
            lambda: view.increaseBrightness(),
            lambda: view.increaseContrast(),
            lambda: view.increaseExposure(),
            lambda: print("LOLCAT"),
        ]
        
        layout = QLayoutMaker(icons, func).make()

        # Swap layout
        self.swapLayout(layout)

    def flipImage(self):
        # Create a image flipper class' instance
        flipper = imageFlipper(self.renderArea, self.outParent)
        
        # Get the respective functions
        func = [
            lambda: flipper.flipLeft(),
            lambda: flipper.flipTop(),
            # lambda: flipper.
            lambda: self.callback(),
        ]
        
        # Get the preffered icons
        icons = loads(self.config.get("singleFolder", "flipper-icons"))
        
        # Swap the layout
        layout = QLayoutMaker(icons, func).make()

        self.swapLayout(layout)

    def swapLayout(self, layout):
        # Get the main widget
        self.central = self.outParent.parent()
        
        # Animation callback
        def animation_callback():
            
            # Hide the area when it is being formatted
            self.outParent.hide()

            new_label.setGeometry(self.outParent.takeWidget().geometry())

            new_label.setLayout(layout)

            self.outParent.setWidget(new_label)
            
            # Show on complete
            self.animation = Animation.fadingAnimation(
                Animation, self.central, 200, True
            )

            self.animation.start()

            self.animation.finished.connect(self.outParent.show)
            
        # Animate
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
        # Get the scroll value
        value = int(
            self.sliderValue.text()
            if value not in [None, ""]
            else self.sliderValue.text()
        )
        
        # Find the degree according to the rotations
        self.interiorFunctions.degree = 90 * self.interiorFunctions.rotations

        self.sliderValue.setText(str(self.interiorFunctions.degree % 360))
        
        # Connect with a new function
        self.sliderValue.textChanged.disconnect()

        self.sliderValue.textChanged.connect(self.rotateLabel)
        
        # Update the value in slider too
        self.slider.setValue(value)
        
        # Start animation
        self.renderArea.start_animation(self.interiorFunctions.degree)


class cropImage:
    SAVE_DIR = "GalleryMan/assets/processed_image.png"

    def __init__(
        self, dir: str, newParent, renderArea: QRotateLabel, outDisplay
    ) -> None:
        
        # Make every args global
        self.directory = dir
        
        self.image = Image.open(self.directory)
        
        self.outDisplay = outDisplay
        
        self.renderArea = renderArea
        
        self.rotations = 0
        
        self.degree = 0
        
        self.newParent = newParent

    def rotate90(self):
        # Add 90 to the degree
        self.degree += 90
        
        # Add rotation
        self.rotations += 1
        
        # Update the text
        self.outDisplay.setText(str(self.degree % 360))
        
        # Start the animation
        self.renderArea.start_animation(self.degree % 360)
        
        # Update the image
        self.updateImage()

    def rotate90Right(self):
        # Subtract the rotation (due to reverse rotation)
        self.degree -= 90

        self.rotations -= 1
        
        # Update the text
        self.outDisplay.setText(str(self.degree % 360))
        
        # Start animation
        self.renderArea.start_animation(self.degree % 360)
        
        # Update the image
        self.updateImage()

    def updateImage(self):
        # Update the pillow image
        self.image = Image.open("GalleryMan/assets/processed_image.png")

    def swapLayout(self, layout):
        # Get the central widget of the QScrollArea
        self.central = self.newParent.parent()
        
        # Callback
        def animation_callback():
            
            # Hide the scrollArea while it is updated
            self.newParent.hide()
            
            new_label.setGeometry(self.newParent.takeWidget().geometry())

            new_label.setLayout(layout)

            self.newParent.setWidget(new_label)
            
            # Show the widget
            self.animation = Animation.fadingAnimation(
                Animation, self.central, 200, True
            )

            self.animation.start()

            self.animation.finished.connect(self.newParent.show)
            
        # Animate
        new_label = QLabel()

        self.animation = Animation.fadingAnimation(Animation, self.central, 300)

        self.animation.start()

        self.animation.finished.connect(animation_callback)

    def save(self, callback):
        # Open the image using PIL
        image = Image.open("GalleryMan/assets/processed_image.png")
        
        # Rotate the image
        image = image.rotate(-(self.degree % 360), expand=1, fillcolor=(255, 0, 0, 1))
        
        # Save the image
        image.save("GalleryMan/assets/processed_image.png")
        
        # Call the callback
        callback()


class textInImage:
    def __init__(self, parent, out_widget, scrollArea) -> None:
        
        # Make every argument global
        self.parent = parent

        self.out_widget = out_widget

        self.scrollArea = scrollArea
        
        # Create graphics
        self.graphics = QGraphicsView(self.parent)
        
        # Call the responser on resize Event
        self.graphics.resizeEvent = self.responser
        
        # Show the graphics
        self.graphics.show()
        
        # Create a dictionary of the styling
        self.storedValue = {
            "color": "#88C0D0",
            "font-family": "Comfortaa",
            "font-size": 11,
        }
        
        # Create a menu
        self.menu = QSliderMenu(self.graphics)
        
        # A button which will show the menui
        startAni = QCustomButton("S", self.graphics).create()

        startAni.setGeometry(QRect(1800, 10, 100, 100))

        startAni.clicked.connect(lambda: self.manageMenu())

        startAni.show()

        self.current = 0

    def updateStyling(self, newValue):
        
        # Change the text with the new text
        self.label.setText(self.storedValue["text"])

        # Resize the box with the new text
        self.resizeToContent(self.label.text())
        
        # Stylings
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
        
    def swapLayout(self, layout):
        
        # Get the central widget
        self.central = self.scrollArea.parent()
        
        # Animation callback
        def animation_callback():
            
            # Hide the scrollarea while it is updated
            self.scrollArea.hide()

            new_label.setGeometry(self.scrollArea.takeWidget().geometry())

            new_label.setLayout(layout)

            self.scrollArea.setWidget(new_label)
            
            # Show the area
            self.animation = Animation.fadingAnimation(
                Animation, self.central, 200, True
            )

            self.animation.start()

            self.animation.finished.connect(self.scrollArea.show)
            
        # Animate
        new_label = QLabel()

        self.animation = Animation.fadingAnimation(Animation, self.central, 300)

        self.animation.start()

        self.animation.finished.connect(animation_callback)

    def update(self, property, label):
        
        # Change the dictonary with the new values
        self.storedValue[property] = label.text()
        
        # Update the styling with the new values
        self.updateStyling(None)

    def createGraphics(self):
        # Create a scene
        self.scene = QGraphicsScene()
        
        # Set geometry
        self.graphics.setGeometry(QRect(0, 0, 1980, 1080))
        
        # Add scene
        self.graphics.setScene(self.scene)
        
        # Add pixmap
        self.scene.addPixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        # Show the graphics
        self.graphics.show()
        
        # Move to the top
        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Create a draggable label
        self.label = DraggableLabel(None)
        
        # Set text
        self.label.setText("Your Text")

        # Stylings
        self.label.setStyleSheet("""
            background-color: transparent;
            font-size: 40px;
            font-family: Comfortaa                         
        """)
        
        # Move to desired location
        self.label.move(QPoint(100 , 100))
        
        # Add to scene
        self.scene.addWidget(self.label)
        
        # Show the label
        self.label.show()

        continueButton = QCustomButton("Continue", self.graphics).create()

        continueButton.clicked.connect(lambda: self.saveText())

        continueButton.setGeometry(QRect(0, 0, 500, 100))

        continueButton.show()

    def resizeToContent(self, text):
        
        # Get the width and the height of the and set size accordingly
        font = QFont(
            self.storedValue["font-family"], int(self.storedValue["font-size"])
        )

        met = QFontMetrics(font)

        width = met.width(text)

        height = met.height()

        self.label.setText(text)

        self.label.setFixedSize(width, height)
        
        self.label.adjustSize()

    def saveText(self):
        
        # Callback
        def callback():
            self.graphics.hide()
            
            self.out_widget.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))
        
        # Open the image
        self.image = Image.open("GalleryMan/assets/processed_image.png")
        
        # Get the geometry
        area = self.graphics.geometry()
        
        # Parse the image 
        image = QImage(area.size(), QImage.Format_ARGB32_Premultiplied)
        
        painter = QPainter(image)
        
        self.scene.render(painter, QRectF(image.rect()), QRectF(area))
        
        painter.end()
        
        # Save the new image
        image.save("GalleryMan/assets/processed_image.png")
        
        # Hide the graphics
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
        
        # Show the menu
        self.menu.show()
        
        # Set alignment
        self.menu.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        for name in ["Width" , "Text" , "Height" , "Color" , "Font Family" , "Font Size"]:
            
            # Create a input and set size and styles accordingly
            inputLabel = QLineEdit()

            inputLabel.setAlignment(Qt.AlignLeft | Qt.AlignTop)

            inputLabel.setPlaceholderText(name)

            inputLabel.setStyleSheet(stylesheet)

            inputLabel.textChanged.connect(partial(self.update, name.lower().replace(' ' , '-') , inputLabel))

            self.menu.addMenu(name , inputLabel)
        
        # Move the menu to outside of the screen
        self.menu.move(QPoint(2000, 0))
        
        # Move it inside the screen with animation
        self.animation = Animation.movingAnimation(
            Animation, self.menu, QPoint(1900 - self.menu.width(), 0), 300
        )

        self.animation.start()

    def responser(self, event: QResizeEvent):
        print(event.size())


class imageFlipper:
    def __init__(self, renderArea, outParent) -> None:
        # Make every args global
        self.renderArea = renderArea

        self.outParent = outParent

        self.image = Image.open("GalleryMan/assets/processed_image.png")

    def flipLeft(self):
        
        # Callback
        def animation_callback():
            
            # Flip the image and set the pixmap (Updated one)
            new_image = self.image.transpose(method=Image.FLIP_LEFT_RIGHT)

            self.renderArea.set_pixmap(self.createPixmap(new_image))

            new_image.save("GalleryMan/assets/processed_image.png")

            self.image = Image.open("GalleryMan/assets/processed_image.png")
            
            # Show the label after a partial hide
            self.animation = Animation.fadingAnimation(
                Animation, self.renderArea, 200, True, startValue=0.5
            )

            self.animation.start()
            
        # Partial hide the label when the image is being processed
        self.animation = Animation.fadingAnimation(
            Animation, self.renderArea, 200, endValue=0.5
        )

        self.animation.start()
        
        # Callback
        self.animation.finished.connect(animation_callback)

    def flipTop(self):
        
        # Animation callback
        def animation_callback():
            
            # Process the image
            new_image = self.image.transpose(method=Image.FLIP_TOP_BOTTOM)

            self.renderArea.set_pixmap(self.createPixmap(new_image))

            new_image.save("GalleryMan/assets/processed_image.png")

            self.image = Image.open("GalleryMan/assets/processed_image.png")
            
            # Partial unhide  
            self.animation = Animation.fadingAnimation(
                Animation, self.renderArea, 200, True, startValue=0.5
            )

            self.animation.start()
            
        # Partial hide when the image is being processed
        self.animation = Animation.fadingAnimation(
            Animation, self.renderArea, 200, endValue=0.5
        )

        self.animation.start()
        
        # Callback
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