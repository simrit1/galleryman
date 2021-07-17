# Importing all the required modules
from math import ceil
from PIL.Image import open
import functools, gc, json
from configparser import ConfigParser
from random import randint
from GalleryMan.utils.readers import change_with_config, read_file
from GalleryMan.assets.QtHelpers import Animation, PopUpMessage, QCustomButton
from PyQt5.QtCore import (
    QAbstractAnimation,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRect,
    QThread,
    QVariant,
    QVariantAnimation,
    pyqtSignal,
    pyqtSlot,
)
from PyQt5.QtGui import QCursor, QKeySequence, QPixmap, QTransform
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QShortcut,
    QSlider,
    QVBoxLayout,
    QWidget,
)
import os
from GalleryMan.assets.QEditorButtons import Cropper, FilterView, PaletteView

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


class CustomLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.clicked.emit()


class singleFolderView:
    def __init__(
        self,
        window: QWidget,
        directory: str,
        config: ConfigParser,
        scroll: QScrollArea,
        application: QMainWindow,
        *args: list[str]
    ) -> None:
        self.scaled = json.loads(config.get("singleFolder", "editor-imageScaled"))

        self.scroll = scroll

        self.application = application

        self.window = window

        self.config = config

        self.application.resizeEvent = self.responser

        self.folders = []

        self.args = args

        self.popup = PopUpMessage()

        self.name = QLabel(self.window)

        self.name.setGeometry(self.args[0].geometry())

        self.name.setText(directory[directory.rindex("/") + 1 :])

        self.name.setAlignment(Qt.AlignCenter)

        self.name.show()

        self.name.setStyleSheet(
            "color: {}; font-family: {}; font-size: {}".format(
                self.config.get("singleFolder", "headerText-color"),
                self.config.get("singleFolder", "headerText-fontFamily"),
                self.config.get("singleFolder", "headerText-fontSize") + "px",
            )
        )

        self.directory = directory

        stylesheet, self.config = change_with_config(
            read_file("GalleryMan/sass/styles.txt"), section="singleFolder"
        )

        self.window.setStyleSheet(stylesheet)

    def remove_self(self):
        self.animation = QParallelAnimationGroup()

        label = self.args[0]

        label.setText("Albums")

        try:
            self.main_window.hide()
        except:
            pass

        for i in [self.labelArea, self.name , self.go_back]:
            opacity = QGraphicsOpacityEffect()

            try:
                i.setGraphicsEffect(opacity)

                animation = QPropertyAnimation(opacity, b"opacity")

                animation.setStartValue(1)

                animation.setEndValue(0)

                animation.setDuration(200)

                self.animation.addAnimation(animation)

                animation.finished.connect(i.hide)

            except:

                pass

        for i in self.args:
            i.show()
            
            self.animation.addAnimation(Animation.fadingAnimation(Animation , i , 200 , True))

        self.animation.start()

        self.animation.finished.connect(self.remove)

    def remove(self):
        self.labelArea.hide()

        self.animation = self.main_window = self.labelArea = self.name = None

        del self.animation, self.main_window, self.labelArea, self.name

        gc.collect()

    def start(self):
        self.go_back = QCustomButton(text=self.config.get("singleFolder" , "back-buttonText")[1:-1] , window=self.window).create()
        
        self.go_back.setStyleSheet("""
            font-size: {}px;
            font-family: {};    
            color: {};                 
        """.format(
            self.config.get("singleFolder" , "back-buttonFontSize"),
            self.config.get("singleFolder" , "back-buttonFontFamily"),
            self.config.get("singleFolder" , "back-buttonColor")
        ))        
        
        self.go_back.setGeometry(QRect(
            int(self.config.get("singleFolder" , "back-buttonTopPadding")),
            int(self.config.get("singleFolder" , "back-buttonLeftPadding")),
            int(self.config.get("singleFolder" , "back-buttonWidth")),
            int(self.config.get("singleFolder" , "back-buttonHeight")),
        ))
        
        self.go_back.setShortcut("Alt+Left")
        
        self.go_back.clicked.connect(self.remove_self)
        
        self.go_back.show()
        
        self.labelArea = QLabel(self.window)

        self.labelArea.show()

        self.labelArea.setGeometry(QRect(0, 100, 1980, 1080))

        card_width = int(self.config.get("singleFolder", "card-width"))

        card_height = int(self.config.get("singleFolder", "card-height"))

        colors = json.loads(self.config.get("singleFolder", "card-color"))

        color_mode = json.loads(self.config.get("singleFolder", "card-mode"))

        self.index = 0

        from pathlib import Path

        dirs = Path(self.directory).rglob("*.png")
              
        self.application.setCursor(Qt.BusyCursor)
        
        for i in dirs:
            i = str(i)
            
            if os.path.isdir("{}/{}".format(self.directory, i)) or i[-3:] not in [
                "png",
                "svg",
                "jpg",
                "jpeg",
            ]:
                continue
                        
            if color_mode == "single":
                self.index = 0
            elif color_mode == "random":
                self.index = randint(0, len(colors) - 1)
            else:
                self.index = (self.index + 1) % len(colors)

            image = CustomLabel(self.labelArea)

            image.setGeometry(QRect(0, 0, card_width, card_height))

            pixmap = QPixmap(i).scaled(
                card_width, card_height,
                transformMode=Qt.SmoothTransformation
            )

            image.setPixmap(pixmap)

            image.setCursor(QCursor(Qt.PointingHandCursor))

            image.setStyleSheet(
                "border: {}px solid {}".format(
                    self.config.get("singleFolder", "card-borderWidth"),
                    colors[self.index],
                )
            )
            
            image.show()
            
            self.folders.append(image)

            image.clicked.connect(
                functools.partial(self.show_image, i)
            )
                             
        self.responser(None) 
        
        self.application.setCursor(Qt.ArrowCursor)       
        
        gc.collect()

    def show_image(self, name):

        self.name = name

        """Editor Box

        Args:
            self.name (str): The file location
        """
        
        #  ___________________________
        # |                           |
        # | Center Pixmap Adjustments |
        # |___________________________|
        #

        # Center Area (Main)
        self.main_window = QLabel(self.application)

        # Set Geometry
        self.main_window.setGeometry(QRect(0, 100, 1980, 1000))

        # QLabel for image
        self.image = QRotateLabel(self.main_window)

        self.dimension = json.loads(
            self.config.get("singleFolder", "editor-imagePadding")
        )
        
        self.geometry = [
            *self.dimension[:2],
            self.application.size().width() - self.dimension[0] - self.dimension[2],
            self.application.size().height() - self.dimension[1] - self.dimension[3],
        ]
        

        # Set The Geometry
        self.image.setGeometry(QRect(*self.geometry))

        self.image.setStyleSheet("background-color: transparent")

        # Set The Pixmap
        os.system('cp "{}" GalleryMan/assets/processed_image.png'.format(self.name))

        self.pixmap = QPixmap("GalleryMan/assets/processed_image.png")

        self.image.set_pixmap(self.pixmap)

        # Again, Scaled Contents are cool :)
        self.image.setScaledContents(self.scaled)
        
        self.central = QLabel(self.application)
    
        self.central.setGeometry(QRect(450 , 850 , 1010 , 140))
        
        self.central.show()
        
        layout = QVBoxLayout(self.central)
        
        self.scrollArea = QScrollArea(self.central)
                
        layout.addWidget(self.scrollArea)
        
        self.buttons = QWidget()
        
        self.buttons.setGeometry(QRect(0 , 850 , 900 , 100))
                
        self.scrollArea.setWidget(self.buttons)
    
        second_layout = QHBoxLayout(self.buttons)
        
        self.buttons.setLayout(second_layout)
        
        # Set fixed spacing between the elements
        second_layout.setSpacing(1)

        #  ___________________________
        # |                           |
        # |    Editor Buttons         |
        # |___________________________|
        #

        icons = json.loads(self.config.get("singleFolder", "editorButtons-icons"))

        i = 0

        functions = [
            self.rotate_image,
            lambda: self.switch_to_cropper(self.name),
            lambda: self.switch_to_filters(self.name),
            lambda: self.switch_to_palette(self.name),
            lambda: self.save_edited(name),
            lambda: self.closeEditor(),
        ]

        # 3. Crop Image
        for icon, icon_color, icon_font_size, icon_family in icons:

            item = QCustomButton(icon, None, True).create()

            item.setStyleSheet(
                "color: {}; font-size: {}px; font-family: {}".format(
                    icon_color, icon_font_size, icon_family
                )
            )

            item.clicked.connect(functions[i])

            i += 1

            second_layout.addWidget(item)

        
        self.buttons.show()

        self.name = "GalleryMan/assets/processed_image.png"

        del icons, icon, icon_color, icon_family, icon_font_size, self.pixmap

        self.new_layout = second_layout

        gc.collect()
        
        self.main_window.show()
        
        self.responser(None)

    def save_edited(self, dir):
        parent = dir[: dir.rindex("/")]

        name = dir[dir.rindex("/") + 1 : -4] + "_edited.png"

        os.system(
            "mv GalleryMan/assets/processed_image.png  {}".format(
                "{}/{}".format(parent, name)
            )
        )

        self.popup.new_msg(self.window, "Image saved as {}".format(name), 200)

        parent = name = None

        del parent, name

        self.closeEditor()

        gc.collect()

    def closeEditor(self):
        self.anim = Animation.fadingAnimation(Animation, self.main_window, 250)

        self.anim.start()

        self.anim.finished.connect(lambda: self.main_window.hide())

    def rotate_image(self):
        self.buttons.hide()
        
        self.image.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        self.new_label = QWidget(self.application)

        width = int(self.config.get("singleFolder", "slider-width"))

        input_width = int(self.config.get("singleFolder", "input-width"))

        padding = int(self.config.get("singleFolder", "item-padding"))

        self.new_label.setGeometry(
            QRect(
                int(self.config.get("singleFolder", "item-leftPadding")),
                310,
                width + padding + input_width + padding,
                100,
            )
        )
        
        self.scrollArea.takeWidget()
        
        self.scrollArea.setWidget(self.new_label)

        self.new_label.setStyleSheet("background-color: transparent;")

        self.layout = QHBoxLayout()

        self.layout.setSpacing(padding)

        self.slider = QSlider(Qt.Horizontal)

        self.slider.setMaximum(360)

        self.slider.setMinimum(0)

        self.slider.setFixedSize(
            width,
            int(self.config.get("singleFolder", "slider-height")),
        )

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

        self.textBox = QLineEdit()

        self.textBox.setPlaceholderText("Image Degree")

        self.textBox.setStyleSheet(
            """
            width: {}px;
            height: {}px;
            background-color: {};
            font-size: {}px;
            font-family: {};
            color: {};
            border-radius: {}px;
            border: {}px solid {};                           
        """.format(
                input_width,
                self.config.get("singleFolder", "input-height"),
                self.config.get("singleFolder", "input-backgroundColor"),
                self.config.get("singleFolder", "input-fontSize"),
                self.config.get("singleFolder", "input-fontFamily"),
                self.config.get("singleFolder", "input-textColor"),
                self.config.get("singleFolder", "input-borderRadius"),
                self.config.get("singleFolder", "input-borderWidth"),
                self.config.get("singleFolder", "input-borderColor"),
            )
        )

        self.textBox.textChanged.connect(self.update_text)

        self.slider.valueChanged.connect(lambda: self.show(self.slider.value()))

        self.layout.addWidget(self.slider)

        self.new_label.setLayout(self.layout)

        self.layout.addWidget(self.textBox)

        self.popup.new_msg(self.window, "Press Enter To Rotate The Image", 200)

        self.shortcut = QShortcut(QKeySequence("Return"), self.window)

        self.shortcut.activated.connect(self.removecropper)

        del self.new_label, width, input_width, padding

        gc.collect()

    def removecropper(self):
        self.shortcut.setKey(QKeySequence())

        value = int(self.textBox.text()) + 180

        image = open("GalleryMan/assets/processed_image.png").convert("RGBA")

        image = image.rotate(value, expand=1, fillcolor=(255, 255, 255, 0))

        image.save("GalleryMan/assets/processed_image.png")

        self.parallel = QParallelAnimationGroup()

        ani = Animation.fadingAnimation(Animation, self.new_label, 400)

        self.parallel.addAnimation(ani)

        anim = Animation.fadingAnimation(Animation, self.buttons, 400, True)

        self.parallel.addAnimation(anim)

        self.parallel.start()

        self.image.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))

        self.parallel.finished.connect(self.switch_to_home)

    def switch_to_home(self):
        self.buttons.show()

        self.new_label.hide()

    def update_text(self):
        curr = self.textBox.text()

        try:
            curr = int(curr)
        except:

            return

        self.slider.setValue(int(curr))

        self.image.start_animation(curr)

    def show(self, deg):
        self.image.start_animation(deg)

        self.textBox.setText(str(deg))

    def switch_to_cropper(self, name):        
        Cropper(self.window, name, self.image, self.config, self.callback_2).create()

        # self.image.show()

    def callback_2(self):
        self.window.setCursor(QCursor(Qt.ArrowCursor))

        self.image.set_pixmap(QPixmap("GalleryMan/assets/processed_image.png"))

    def switch_to_filters(self, name):
        self.buttons.hide()

        self.new_label = QWidget(self.application)
        
        self.new_label.setGeometry(QRect(0 , 850 , 2000 , 100))
        
        self.scrollArea.takeWidget()
                
        self.scrollArea.setWidget(self.new_label)

        # self.new_label.setStyleSheet("background-color: transparent;")

        buttons = FilterView(
            self.window,
            name,
            self.image,
            json.loads(self.config.get("singleFolder", "filters-colorIcons")),
            self.callback,
        ).create()

        self.new_label.setLayout(buttons)
        
        self.new_label.show()
        
        self.responser(None)

    def switch_to_palette(self, name):
        self.buttons.hide()

        self.new_label = QLabel(self.main_window)

        self.new_label.setGeometry(self.buttons.geometry())

        self.new_label.show()

        self.new_label.setStyleSheet("background-color: transparent")

        buttons = PaletteView(
            self.main_window, name, self.image, self.config, self.callback
        ).create()

        self.new_label.setLayout(buttons)

    def callback(self):
        def finish():
            self.new_label.hide()

            self.buttons.show()

        self.ani = QParallelAnimationGroup()

        self.ani.addAnimation(Animation.fadingAnimation(Animation, self.new_label, 200))

        self.ani.addAnimation(
            Animation.fadingAnimation(Animation, self.buttons, 200, True)
        )

        self.ani.start()

        self.ani.finished.connect(finish)

    def responser(self, _):
        self.width = self.application.size().width()
        
        card_width = int(self.config.get("singleFolder", "card-width"))

        card_height = int(self.config.get("singleFolder", "card-height"))

        card_padding = int(self.config.get("singleFolder", "card-padding"))

        x, y = 40, 100

        self.animations = QParallelAnimationGroup()

        for i in self.folders:
            ani = QPropertyAnimation(i, b"pos")

            ani.setStartValue(i.pos())

            ani.setEndValue(QPoint(x, y))

            ani.setDuration(100)

            x += card_width + card_padding

            self.animations.addAnimation(ani)

            if x > self.width - card_width:
                x = 40

                y += card_height + card_padding
            
        self.perline = (self.width - card_width) // card_width
        
        
        try:
            self.new_width = (50 / 100) * self.width
            
            self.central.setGeometry(QRect(
                self.new_width // 2,
                self.central.y(),
                self.new_width, 
                self.central.height()
            ))
        
        except:
            pass
        
        try:
            self.new_width = (50 / 100) * self.width
            
            self.new_label.setGeometry(QRect(
                self.new_width // 2,
                self.new_label.y(),
                self.new_width, 
                self.new_label.height()
            ))
            
            self.scrollArea.show()
            
            self.new_label.show()
        except:
            
            pass
        
        self.width = 300 + card_height * ceil(len(self.folders) / max(self.perline , 1))
        
        self.window.setFixedHeight(self.width)
        
        self.labelArea.setFixedHeight(self.width)
        
        try:        
            self.geometry = [
                *self.dimension[:2],
                self.application.size().width() - self.dimension[0] - self.dimension[2],
                self.application.size().height() - self.dimension[1] - self.dimension[3],
            ]
            
            # Set The Geometry
            self.image.setGeometry(QRect(*self.geometry))
        
        except:
            
            pass
        
        self.animations.start()

    def get_first(self, dir: str) -> str:
        """Returns the first image in the folder, or None if no image is available

        Args:
            dir (str): [description]

        Returns:
            str: [description]
        """

        # Iterate through all the files and folders in the directory
        for i in os.listdir(dir):

            # Check if the image is a supported one
            if i[-3:] in ["png", "jpeg", "jpg", "webp"] and not os.path.isdir(
                "{}/{}".format(dir, i)
            ):
                return "{}/{}".format(dir, i)

        return None
